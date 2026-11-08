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

1. Fork and clone the repository (see [Setup](00-setup.md)).
2. Create a branch:

   ```shell
   git switch -c add-readme-note
   ```

3. Change a file. Commit the change:

   ```shell
   git add README.md
   git commit -m "Add a note to the README"
   ```

4. Push the branch:

   ```shell
   git push -u origin add-readme-note
   ```

5. On GitHub, open a pull request into `main` of your fork. Merge it.

Concepts: repository, commit, branch, remote, fork, pull request, merge.

## Episode 3: Run the app

Goal: you run all three parts in containers and call the API.

Run each command from the repository root. The commands work in a macOS terminal and in PowerShell.

On Windows PowerShell 5.1, `curl` is an alias for a different command. Type `curl.exe` in place of `curl`.

1. Create a network, so containers can find each other by name:

   ```shell
   docker network create taskboard
   ```

2. Start PostgreSQL. The init file creates the `tasks` table:

   ```shell
   docker run -d --name database --network taskboard -e POSTGRES_DB=tasks -e POSTGRES_USER=tasks -e POSTGRES_PASSWORD=change-me -v "${PWD}/database/init.sql:/docker-entrypoint-initdb.d/001-init.sql:ro" postgres:16-alpine
   ```

3. Start the backend in a Python container:

   ```shell
   docker run -d --name backend --network taskboard -p 8000:8000 -e DB_HOST=database -e DB_PASSWORD=change-me -v "${PWD}/backend:/app" -w /app python:3.12-slim sh -c "pip install -r requirements.txt && python app.py"
   ```

4. Start the frontend. Nginx sends `/api/` requests to the container named `backend`:

   ```shell
   docker run -d --name frontend --network taskboard -p 8080:80 -v "${PWD}/frontend/nginx.conf:/etc/nginx/conf.d/default.conf:ro" -v "${PWD}/frontend:/usr/share/nginx/html:ro" nginx:1.27-alpine
   ```

5. Wait until the backend is ready. Repeat the command until it shows `"ready"`:

   ```shell
   curl http://localhost:8000/readyz
   ```

6. Open http://localhost:8080 and add a task.
7. Call the API directly:

   ```shell
   curl http://localhost:8000/api/tasks
   ```

8. Clean up:

   ```shell
   docker rm -f frontend backend database
   docker network rm taskboard
   ```

Concepts: container, image, port mapping, volume mount, environment variable, container network, health check.

## Episode 4: Add a feature with a test

Goal: you add `DELETE /api/tasks/<id>` and prove it works with a test.

Requirements:

- A delete of an existing task returns status 200 and the deleted task as JSON.
- A delete of a missing task returns status 404.
- The frontend shows a **Delete** button on each task.

Steps:

1. Create a branch named `delete-task`.
2. Add the endpoint to `backend/app.py`. Use the `PATCH` endpoint as a model. Use `DELETE ... RETURNING`.
3. Add two tests to `backend/test_app.py`. Use `unittest.mock.patch` to replace `connect_to_database`. The tests then do not need a database. Add `MagicMock` and `patch` to the imports. Add the `fake_database` helper shown in Episode 4.
4. Run the tests:

   ```shell
   docker compose -f tools/compose.yaml run --rm python-test
   ```

5. Add the button in `frontend/app.js`.
6. Test by hand with the Episode 3 commands.
7. Push the branch. Open a pull request. Merge it.

Concepts: REST methods, HTTP status codes, unit test, mock, test-first thinking, code review.

## Episode 5: Containers

Goal: each part has its own image, and one command starts the full stack.

1. Write `backend/Dockerfile`:
   - Start from `python:3.12-slim`.
   - Install `requirements.txt` before you copy the code, so Docker can cache the layer.
   - Run as a non-root user.
   - Start with `gunicorn --bind=0.0.0.0:8000 app:app`.
2. Write `frontend/Dockerfile`. Start from `nginx:1.27-alpine`. Copy `nginx.conf` and the static files.
3. Write `database/Dockerfile`. Start from `postgres:16-alpine`. Copy `init.sql` to `/docker-entrypoint-initdb.d/`.
4. Write `compose.yaml` with three services: `database`, `backend`, `frontend`.
   - Read the password from `.env`. Never commit `.env`.
   - Add a `pg_isready` health check to the database.
   - Start the backend only after the database is healthy.
   - Give the backend no `ports:` entry. The frontend reaches it over the Compose network by service name. A published backend port works on your laptop, but Episode 9 shows it also defeats the VM firewall.
   - Map frontend port 80 to host port 8080.
5. Copy the example environment file:

   ```shell
   cp .env.example .env
   ```

6. Start the stack:

   ```shell
   docker compose up --build
   ```

7. Open http://localhost:8080. Add and delete a task.
8. Stop the stack and delete its volume:

   ```shell
   docker compose down -v
   ```

Concepts: Dockerfile, layer, build cache, base image, image tag, non-root user, Compose service, named volume, `depends_on`.

## Episode 6: Continuous Integration

Goal: GitHub runs the tests and builds the images on every pull request.

1. Create `.github/workflows/ci.yml`.
2. Run it on `pull_request` and on `push` to `main`.
3. Give the workflow read-only permissions: `contents: read`.
4. Add a `test` job: check out the code, set up Python 3.12, install the requirements, run `python -m unittest discover -s backend -v`.
5. Add a `build` job: run `docker compose build`. Set `DB_PASSWORD` in the job, because Compose requires it.
6. Open a pull request. Watch both jobs pass.
7. Break a test on purpose. Watch the check fail. Fix it.

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
