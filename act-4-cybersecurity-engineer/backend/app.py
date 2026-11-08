import os
import time
from datetime import datetime, timedelta, timezone
from functools import wraps

import bcrypt
import jwt
import psycopg
import psycopg.errors
from flask import Flask, g, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from psycopg.rows import dict_row

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "app_http_requests_total",
    "HTTP requests handled by the backend",
    ["method", "endpoint", "status"],
)
REQUEST_DURATION = Histogram(
    "app_http_request_duration_seconds",
    "Time spent handling backend HTTP requests",
    ["method", "endpoint"],
)
MAX_WORK_UNITS = 5_000_000
JWT_ALGORITHM = "HS256"
TOKEN_LIFETIME = timedelta(hours=24)


def connect_to_database():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "tasks"),
        user=os.getenv("DB_USER", "tasks"),
        password=os.environ["DB_PASSWORD"],
        connect_timeout=3,
        row_factory=dict_row,
    )


def get_jwt_secret():
    return os.environ["JWT_SECRET"]


def require_auth(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify(error="Authentication required."), 401

        try:
            payload = jwt.decode(
                header.removeprefix("Bearer "), get_jwt_secret(), algorithms=[JWT_ALGORITHM]
            )
        except jwt.InvalidTokenError:
            return jsonify(error="Invalid or expired token."), 401

        g.user_id = int(payload["sub"])
        return view(*args, **kwargs)

    return wrapped


@app.before_request
def start_request_timer():
    g.request_started_at = time.perf_counter()


@app.after_request
def record_request(response):
    if request.endpoint != "metrics":
        endpoint = request.endpoint or "unknown"
        REQUEST_COUNT.labels(request.method, endpoint, str(response.status_code)).inc()
        REQUEST_DURATION.labels(request.method, endpoint).observe(
            time.perf_counter() - g.request_started_at
        )
    return response


@app.errorhandler(psycopg.Error)
def handle_database_error(_error):
    return jsonify(error="Database is unavailable."), 503


@app.get("/healthz")
def health():
    return jsonify(status="ok")


@app.get("/readyz")
def ready():
    try:
        with connect_to_database() as connection:
            connection.execute("SELECT 1")
    except (psycopg.Error, KeyError):
        return jsonify(status="not ready"), 503
    return jsonify(status="ready")


@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.post("/api/auth/register")
def register():
    data = request.get_json(silent=True)
    username = data.get("username") if isinstance(data, dict) else None
    password = data.get("password") if isinstance(data, dict) else None

    if not isinstance(username, str) or not 3 <= len(username) <= 32:
        return jsonify(error="Username must contain 3 to 32 characters."), 400
    if not isinstance(password, str) or len(password) < 8:
        return jsonify(error="Password must contain at least 8 characters."), 400

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        with connect_to_database() as connection:
            user = connection.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id, username",
                (username, password_hash),
            ).fetchone()
    except psycopg.errors.UniqueViolation:
        return jsonify(error="Username is already taken."), 409
    return jsonify(user), 201


@app.post("/api/auth/login")
def login():
    data = request.get_json(silent=True)
    username = data.get("username") if isinstance(data, dict) else None
    password = data.get("password") if isinstance(data, dict) else None

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify(error="Username and password are required."), 400

    with connect_to_database() as connection:
        user = connection.execute(
            "SELECT id, password_hash FROM users WHERE username = %s", (username,)
        ).fetchone()

    if user is None or not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return jsonify(error="Invalid username or password."), 401

    expires_at = datetime.now(timezone.utc) + TOKEN_LIFETIME
    token = jwt.encode(
        {"sub": str(user["id"]), "exp": expires_at}, get_jwt_secret(), algorithm=JWT_ALGORITHM
    )
    return jsonify(token=token)


@app.get("/api/tasks")
@require_auth
def list_tasks():
    with connect_to_database() as connection:
        tasks = connection.execute(
            "SELECT id, title, done FROM tasks WHERE owner_id = %s ORDER BY id DESC",
            (g.user_id,),
        ).fetchall()
    return jsonify(tasks)


@app.post("/api/tasks")
@require_auth
def create_task():
    data = request.get_json(silent=True)
    title = data.get("title") if isinstance(data, dict) else None

    if not isinstance(title, str) or not title.strip() or len(title.strip()) > 120:
        return jsonify(error="Title must contain 1 to 120 characters."), 400

    with connect_to_database() as connection:
        task = connection.execute(
            "INSERT INTO tasks (title, owner_id) VALUES (%s, %s) RETURNING id, title, done",
            (title.strip(), g.user_id),
        ).fetchone()
    return jsonify(task), 201


@app.patch("/api/tasks/<int:task_id>")
@require_auth
def update_task(task_id):
    data = request.get_json(silent=True)
    done = data.get("done") if isinstance(data, dict) else None

    if not isinstance(done, bool):
        return jsonify(error="Done must be true or false."), 400

    with connect_to_database() as connection:
        task = connection.execute(
            "UPDATE tasks SET done = %s WHERE id = %s AND owner_id = %s RETURNING id, title, done",
            (done, task_id, g.user_id),
        ).fetchone()

    if task is None:
        return jsonify(error="Task not found."), 404
    return jsonify(task)


@app.delete("/api/tasks/<int:task_id>")
@require_auth
def delete_task(task_id):
    with connect_to_database() as connection:
        task = connection.execute(
            "DELETE FROM tasks WHERE id = %s AND owner_id = %s RETURNING id, title, done",
            (task_id, g.user_id),
        ).fetchone()

    if task is None:
        return jsonify(error="Task not found."), 404
    return jsonify(task)


@app.get("/api/tasks/search")
@require_auth
def search_tasks():
    term = request.args.get("q", "")
    with connect_to_database() as connection:
        tasks = connection.execute(
            "SELECT id, title, done FROM tasks WHERE owner_id = %s AND title LIKE %s ORDER BY id DESC",
            (g.user_id, f"%{term}%"),
        ).fetchall()
    return jsonify(tasks)


@app.get("/api/demo/work")
def demo_work():
    try:
        units = int(request.args.get("units", "1000000"))
    except ValueError:
        return jsonify(error="Units must be a whole number."), 400

    if not 1 <= units <= MAX_WORK_UNITS:
        return jsonify(error=f"Units must be between 1 and {MAX_WORK_UNITS}."), 400

    checksum = sum(number * number for number in range(units))
    return jsonify(units=units, checksum=checksum)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
