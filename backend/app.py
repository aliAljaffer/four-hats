import os
import time

import psycopg
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


@app.get("/api/tasks")
def list_tasks():
    with connect_to_database() as connection:
        tasks = connection.execute(
            "SELECT id, title, done FROM tasks ORDER BY id DESC"
        ).fetchall()
    return jsonify(tasks)


@app.post("/api/tasks")
def create_task():
    data = request.get_json(silent=True)
    title = data.get("title") if isinstance(data, dict) else None

    if not isinstance(title, str) or not title.strip() or len(title.strip()) > 120:
        return jsonify(error="Title must contain 1 to 120 characters."), 400

    with connect_to_database() as connection:
        task = connection.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, done",
            (title.strip(),),
        ).fetchone()
    return jsonify(task), 201


@app.patch("/api/tasks/<int:task_id>")
def update_task(task_id):
    data = request.get_json(silent=True)
    done = data.get("done") if isinstance(data, dict) else None

    if not isinstance(done, bool):
        return jsonify(error="Done must be true or false."), 400

    with connect_to_database() as connection:
        task = connection.execute(
            "UPDATE tasks SET done = %s WHERE id = %s RETURNING id, title, done",
            (done, task_id),
        ).fetchone()

    if task is None:
        return jsonify(error="Task not found."), 404
    return jsonify(task)


@app.get("/api/tasks/search")
def search_tasks():
    term = request.args.get("q", "")
    with connect_to_database() as connection:
        # Intentionally vulnerable to SQL injection; Act 4 finds and fixes this.
        tasks = connection.execute(
            f"SELECT id, title, done FROM tasks WHERE title LIKE '%{term}%' ORDER BY id DESC"
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
    app.run(host="0.0.0.0", port=8000)
