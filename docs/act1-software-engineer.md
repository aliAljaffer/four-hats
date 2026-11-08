# Act 1: Software Engineer (Episodes 2 to 6)

## Your assignment

| | |
|---|---|
| Role | New Software Engineer |
| Previously | Episodes 0 and 1 introduced the roles and set up your laptop. |
| Task | Users cannot delete a task. The app has three tests for demo work and metrics. It has no feature tests, no container images, and no automated checks. |
| Goal | Ship a delete feature with a test, package the app in containers, and run checks on every pull request. |
| Done when | A merged pull request, a stack that starts with `docker compose up`, and a green CI check. |
| Start here | Fork the starter repository. Act 1 needs only the Episode 1 setup. |

Try each task first. Open **Show solution** for that task only when you are stuck. The last line in each solution links to the `solved` branch. Use that link as a last resort.

## What a Software Engineer does

A Software Engineer turns requirements into working code. In a team, you:

- Write features and fix bugs.
- Write tests, so changes do not break old behavior.
- Review other people's code in pull requests.
- Package the app, so other teams can run it.
- Keep CI green: every change must build and pass the tests.

Job titles: Software Engineer, Backend Developer, Full-Stack Developer.

## The app

A task board with three parts:

| Part | Technology | Folder |
|---|---|---|
| Frontend | HTML, CSS, JavaScript, served by Nginx | `frontend/` |
| Backend | Python Flask API | `backend/` |
| Database | PostgreSQL | `database/` |

Backend endpoints:

| Method | Path | Purpose |
|---|---|---|
| GET | `/healthz` | The process is alive |
| GET | `/readyz` | The database is reachable |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/tasks` | List tasks |
| POST | `/api/tasks` | Create a task |
| PATCH | `/api/tasks/<id>` | Mark a task done or not done |
| GET | `/api/tasks/search?q=` | Search tasks by title |
| GET | `/api/demo/work` | CPU work for the autoscaling demo |

## Episode 2: Git and GitHub

Goal: you can work on a branch and open a pull request.

#### Task 1: Fork the repository

Fork the repository on GitHub.

<details>
<summary>Show solution</summary>

Open https://github.com/aliAljaffer/four-hats and select **Fork**.

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

#### Task 2: Clone your fork

Clone your fork to your laptop. Replace `YOUR_USERNAME` with your GitHub username.

<details>
<summary>Show solution</summary>

```shell
git clone https://github.com/YOUR_USERNAME/four-hats.git
cd four-hats
```

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

#### Task 3: Create a branch

Create a branch named `add-readme-note`.

<details>
<summary>Show solution</summary>

```shell
git switch -c add-readme-note
```

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

#### Task 4: Commit a change

Change a file and commit the change.

<details>
<summary>Show solution</summary>

```shell
git add README.md
git commit -m "Add a note to the README"
```

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

#### Task 5: Push the branch

Push the branch to your fork.

<details>
<summary>Show solution</summary>

```shell
git push -u origin add-readme-note
```

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

#### Task 6: Open and merge a pull request

On GitHub, open a pull request into `main` of your fork. Merge it.

<details>
<summary>Show solution</summary>

Open your fork on GitHub. Select **Compare and pull request** for the `add-readme-note` branch. Set the base branch to `main`. Select **Create pull request**. Select **Merge pull request**.

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

Concepts: repository, commit, branch, remote, fork, pull request, merge.

## Episode 3: Run the app

Goal: you run all three parts in containers and call the API.

If another program uses port 8000 or 8080, use 18000 or 18080 in the commands and URLs. The container port does not change.

#### Task 1: Create a network

Create a network, so containers can find each other by name.

<details>
<summary>Show solution</summary>

```shell
docker network create taskboard
```

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

#### Task 2: Start PostgreSQL

Start PostgreSQL. The init file creates the `tasks` table.

<details>
<summary>Show solution</summary>

```shell
docker run -d --name database --network taskboard -e POSTGRES_DB=tasks -e POSTGRES_USER=tasks -e POSTGRES_PASSWORD=change-me -v "${PWD}/database/init.sql:/docker-entrypoint-initdb.d/001-init.sql:ro" postgres:16-alpine
```

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

#### Task 3: Start the backend

Start the backend in a Python container.

<details>
<summary>Show solution</summary>

```shell
docker run -d --name backend --network taskboard -p 8000:8000 -e DB_HOST=database -e DB_PASSWORD=change-me -v "${PWD}/backend:/app" -w /app python:3.12-slim sh -c "pip install -r requirements.txt && python app.py"
```

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

#### Task 4: Start the frontend

Start the frontend. Nginx sends `/api/` requests to the container named `backend`.

<details>
<summary>Show solution</summary>

```shell
docker run -d --name frontend --network taskboard -p 8080:80 -v "${PWD}/frontend/nginx.conf:/etc/nginx/conf.d/default.conf:ro" -v "${PWD}/frontend:/usr/share/nginx/html:ro" nginx:1.27-alpine
```

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

#### Task 5: Wait until the backend is ready

Wait until the backend is ready.

<details>
<summary>Show solution</summary>

Repeat the command until it shows `"ready"`:

```shell
curl http://localhost:8000/readyz
```

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

#### Task 6: Open the app

Open http://localhost:8080 and add a task.

<details>
<summary>Show solution</summary>

Open http://localhost:8080 in a browser. Type a task title. Select the add button. The task appears in the list.

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

#### Task 7: Call the API directly

Call the API directly.

<details>
<summary>Show solution</summary>

```shell
curl http://localhost:8000/api/tasks
```

On Windows PowerShell 5.1, use `curl.exe` in place of `curl`.

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

#### Task 8: Clean up

Clean up the containers and the network.

<details>
<summary>Show solution</summary>

```shell
docker rm -f frontend backend database
docker network rm taskboard
```

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

Concepts: container, image, port mapping, volume mount, environment variable, container network, health check.

## Episode 4: Add a feature with a test

Goal: you add `DELETE /api/tasks/<id>` and prove it works with a test.

Requirements:

- A delete of an existing task returns status 200 and the deleted task as JSON.
- A delete of a missing task returns status 404.
- The frontend shows a **Delete** button on each task.

#### Task 1: Create a branch

Create a branch named `delete-task`.

<details>
<summary>Show solution</summary>

```shell
git switch -c delete-task
```

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

#### Task 2: Add the DELETE endpoint

Add the endpoint to `backend/app.py`. Use the `PATCH` endpoint as a model. Use `DELETE ... RETURNING`.

<details>
<summary>Show solution</summary>

```python
@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    with connect_to_database() as connection:
        task = connection.execute(
            "DELETE FROM tasks WHERE id = %s RETURNING id, title, done",
            (task_id,),
        ).fetchone()

    if task is None:
        return jsonify(error="Task not found."), 404
    return jsonify(task)
```

Last resort: [open the solved backend/app.py](https://github.com/aliAljaffer/four-hats/blob/solved/act-1-software-engineer/backend/app.py)

</details>

#### Task 3: Add two tests

Add two tests to `backend/test_app.py`. Use `unittest.mock.patch` to replace `connect_to_database`. The tests then do not need a database. Add `MagicMock` and `patch` to the imports. Add the `fake_database` helper.

<details>
<summary>Show solution</summary>

Add the imports and the helper:

```python
from unittest.mock import MagicMock, patch


def fake_database(row):
    connection = MagicMock()
    connection.__enter__.return_value.execute.return_value.fetchone.return_value = row
    return connection
```

Add the two tests to the `AppTests` class:

```python
def test_delete_task_returns_deleted_task(self):
    task = {"id": 7, "title": "Write tests", "done": False}

    with patch("app.connect_to_database", return_value=fake_database(task)):
        response = self.client.delete("/api/tasks/7")

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json, task)

def test_delete_missing_task_returns_404(self):
    with patch("app.connect_to_database", return_value=fake_database(None)):
        response = self.client.delete("/api/tasks/999")

    self.assertEqual(response.status_code, 404)
```

Last resort: [open the solved backend/test_app.py](https://github.com/aliAljaffer/four-hats/blob/solved/act-1-software-engineer/backend/test_app.py)

</details>

#### Task 4: Run the tests

Run the tests.

<details>
<summary>Show solution</summary>

```shell
docker compose -f tools/compose.yaml run --rm python-test
```

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

#### Task 5: Add the Delete button

Add the button in `frontend/app.js`.

<details>
<summary>Show solution</summary>

```javascript
const deleteButton = document.createElement("button");
deleteButton.type = "button";
deleteButton.className = "delete";
deleteButton.textContent = "Delete";
deleteButton.setAttribute("aria-label", `Delete ${task.title}`);

deleteButton.addEventListener("click", async () => {
  try {
    await request(`/api/tasks/${task.id}`, { method: "DELETE" });
    await loadTasks();
  } catch (error) {
    showStatus(error.message, true);
  }
});

item.append(checkbox, title, deleteButton);
```

Replace the existing `item.append(checkbox, title);` line with `item.append(checkbox, title, deleteButton);`.

Last resort: [open the solved frontend/app.js](https://github.com/aliAljaffer/four-hats/blob/solved/act-1-software-engineer/frontend/app.js)

</details>

#### Task 6: Test by hand

Test by hand with the Episode 3 commands.

<details>
<summary>Show solution</summary>

Start the database, backend, and frontend with the Episode 3 commands. Open http://localhost:8080. Add a task. Select **Delete**. The task disappears.

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

#### Task 7: Push and open a pull request

Push the branch. Open a pull request. Merge it.

<details>
<summary>Show solution</summary>

```shell
git add backend/app.py backend/test_app.py frontend/app.js
git commit -m "Add DELETE endpoint for tasks"
git push -u origin delete-task
```

Open a pull request on GitHub. Merge it.

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

Concepts: REST methods, HTTP status codes, unit test, mock, test-first thinking, code review.

## Episode 5: Containers

Goal: each part has its own image, and one command starts the full stack.

#### Task 1: Write the backend Dockerfile

Write `backend/Dockerfile`.

Requirements:

- Start from `python:3.12-slim`.
- Install `requirements.txt` before you copy the code, so Docker can cache the layer.
- Run as a non-root user.
- Start with `gunicorn --bind=0.0.0.0:8000 app:app`.

<details>
<summary>Show solution</summary>

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd --system app \
    && useradd --system --gid app --home-dir /app app

COPY --chown=app:app app.py .

USER app
EXPOSE 8000

CMD ["gunicorn", "--bind=0.0.0.0:8000", "--workers=1", "app:app"]
```

Last resort: [open the solved backend/Dockerfile](https://github.com/aliAljaffer/four-hats/blob/solved/act-1-software-engineer/backend/Dockerfile)

</details>

#### Task 2: Write the frontend Dockerfile

Write `frontend/Dockerfile`. Start from `nginx:1.27-alpine`. Copy `nginx.conf` and the static files.

<details>
<summary>Show solution</summary>

```dockerfile
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html styles.css app.js /usr/share/nginx/html/

EXPOSE 80
```

Last resort: [open the solved frontend/Dockerfile](https://github.com/aliAljaffer/four-hats/blob/solved/act-1-software-engineer/frontend/Dockerfile)

</details>

#### Task 3: Write the database Dockerfile

Write `database/Dockerfile`. Start from `postgres:16-alpine`. Copy `init.sql` to `/docker-entrypoint-initdb.d/`.

<details>
<summary>Show solution</summary>

```dockerfile
FROM postgres:16-alpine

COPY init.sql /docker-entrypoint-initdb.d/001-init.sql
```

Last resort: [open the solved database/Dockerfile](https://github.com/aliAljaffer/four-hats/blob/solved/act-1-software-engineer/database/Dockerfile)

</details>

#### Task 4: Write the Compose file

Write `compose.yaml` with three services: `database`, `backend`, `frontend`.

Requirements:

- Read the password from `.env`. Never commit `.env`.
- Add a `pg_isready` health check to the database.
- Start the backend only after the database is healthy.
- Give the backend no `ports:` entry. The frontend reaches it over the Compose network by service name. A published backend port works on your laptop, but Episode 9 shows it also defeats the VM firewall.
- Map frontend port 80 to host port 8080.

<details>
<summary>Show solution</summary>

```yaml
services:
  database:
    build: ./database
    environment:
      POSTGRES_DB: tasks
      POSTGRES_USER: tasks
      POSTGRES_PASSWORD: ${DB_PASSWORD:?Set DB_PASSWORD in .env}
    volumes:
      - database-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tasks -d tasks"]
      interval: 5s
      timeout: 3s
      retries: 10

  backend:
    build: ./backend
    environment:
      DB_HOST: database
      DB_NAME: tasks
      DB_USER: tasks
      DB_PASSWORD: ${DB_PASSWORD:?Set DB_PASSWORD in .env}
    depends_on:
      database:
        condition: service_healthy

  frontend:
    build: ./frontend
    ports:
      - "8080:80"
    depends_on:
      - backend

volumes:
  database-data:
```

Last resort: [open the solved compose.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-1-software-engineer/compose.yaml)

</details>

#### Task 5: Copy the environment file

Copy the example environment file.

<details>
<summary>Show solution</summary>

```shell
cp .env.example .env
```

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

#### Task 6: Start the stack

Start the stack.

<details>
<summary>Show solution</summary>

If port 8080 is in use, change the frontend mapping in `compose.yaml` to `"18080:80"` and open `http://localhost:18080`.

```shell
docker compose up --build
```

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

#### Task 7: Test the app

Open http://localhost:8080. Add and delete a task.

<details>
<summary>Show solution</summary>

Open http://localhost:8080 in a browser. Add a task. Delete the task. Both actions must work.

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

#### Task 8: Stop the stack

Stop the stack and delete its volume.

<details>
<summary>Show solution</summary>

```shell
docker compose down -v
```

Last resort: [open the solved Act 1 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-1-software-engineer)

</details>

Concepts: Dockerfile, layer, build cache, base image, image tag, non-root user, Compose service, named volume, `depends_on`.

## Episode 6: Continuous Integration

Goal: GitHub runs the tests and builds the images on every pull request.

#### Task 1: Create the workflow file

Create `.github/workflows/ci.yml`. Run it on `pull_request` and on `push` to `main`.

<details>
<summary>Show solution</summary>

```shell
mkdir -p .github/workflows
```

```yaml
name: CI

on:
  pull_request:
  push:
    branches:
      - main
```

Last resort: [open the solved CI workflow](https://github.com/aliAljaffer/four-hats/blob/solved/act-1-software-engineer/.github/workflows/ci.yml)

</details>

#### Task 2: Set permissions

Give the workflow read-only permissions: `contents: read`.

<details>
<summary>Show solution</summary>

```yaml
permissions:
  contents: read
```

Last resort: [open the solved CI workflow](https://github.com/aliAljaffer/four-hats/blob/solved/act-1-software-engineer/.github/workflows/ci.yml)

</details>

#### Task 3: Add the test job

Add a `test` job: check out the code, set up Python 3.12, install the requirements, run `python -m unittest discover -s backend -v`.

<details>
<summary>Show solution</summary>

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - run: pip install -r backend/requirements.txt
      - run: python -m unittest discover -s backend -v
```

Last resort: [open the solved CI workflow](https://github.com/aliAljaffer/four-hats/blob/solved/act-1-software-engineer/.github/workflows/ci.yml)

</details>

#### Task 4: Add the build job

Add a `build` job: run `docker compose build`. Set `DB_PASSWORD` in the job, because Compose requires it.

<details>
<summary>Show solution</summary>

```yaml
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker compose build
        env:
          DB_PASSWORD: ci-only
```

The four fragments form one file. `test:` and `build:` are two entries under `jobs:`, at the same indentation.

Last resort: [open the solved CI workflow](https://github.com/aliAljaffer/four-hats/blob/solved/act-1-software-engineer/.github/workflows/ci.yml)

</details>

#### Task 5: Open a pull request

Open a pull request. Watch both jobs pass.

<details>
<summary>Show solution</summary>

```shell
git switch -c add-ci
git add .github/workflows/ci.yml
git commit -m "Add CI workflow"
git push -u origin add-ci
```

Open a pull request on GitHub. Both jobs must pass.

Last resort: [open the solved CI workflow](https://github.com/aliAljaffer/four-hats/blob/solved/act-1-software-engineer/.github/workflows/ci.yml)

</details>

#### Task 6: Break a test on purpose

Break a test on purpose. Watch the check fail. Fix it.

<details>
<summary>Show solution</summary>

Change one assertion in `backend/test_app.py`. For example, change `self.assertEqual(response.status_code, 200)` to `self.assertEqual(response.status_code, 201)`. Commit and push. The test job fails. Change the assertion back. Commit and push. The test job passes.

Last resort: [open the solved backend/test_app.py](https://github.com/aliAljaffer/four-hats/blob/solved/act-1-software-engineer/backend/test_app.py)

</details>

Concepts: CI, workflow, job, step, runner, trigger, least-privilege permissions, status check.

## Solution

The finished Act 1 is in the `solved` branch of this repository, folder `act-1-software-engineer/`.

## Act review

| | |
|---|---|
| Task | Users could not delete a task, and nothing was tested, packaged, or checked. |
| What you did | Added `DELETE /api/tasks/<id>` with a mocked unit test, wrote Dockerfiles and a Compose file, and built a GitHub Actions CI workflow. |
| What you achieved | A tested, containerized app that starts with one command, with every pull request checked. |
| What comes next | The Cloud Engineer finds a place to run it (Act 2). |

**Resume after Act 1:** use the headline "Junior Software Engineer". Add the Act 1 rows of the [skills ledger](../cv/skills-ledger.md) to your CV.
