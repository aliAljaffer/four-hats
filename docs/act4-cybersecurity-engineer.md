# Act 4: Cybersecurity Engineer (Episodes 20 to 25)

## Your assignment

| | |
|---|---|
| Role | New Cybersecurity Engineer |
| Previously | The DevOps team deployed the app to Kubernetes with GitOps, autoscaling, and monitoring. |
| Task | The backend ships a search endpoint that builds SQL from user input, nobody has tested it, and no part of the app checks who is allowed to change what. |
| Goal | Think and act like an attacker to find the SQL injection, then switch hats and fix it, prove the fix with automated scans, find and fix a second real flaw, and put the app's secrets safely in Git. |
| Done when | `sqlmap` finds nothing on the fixed endpoint, a Pod without an allow rule cannot reach the database, Semgrep, Trivy, and ZAP all run clean or with recorded findings, one user can no longer modify another's task, and every secret the app needs is a committed `SealedSecret`. |
| Start here | Fork the starter repository. Copy `act-3-devops-engineer/` from the `solved` branch into your fork. Keep the starter `tools/` folder. Install Docker Desktop and Minikube. You need a second Minikube profile for the policy check in Episode 22. |

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

If you start Act 4 from the `act-3-devops-engineer/` folder, copy two files from the starter repository into your fork. Copy `kubernetes/sealed-secrets/controller.yaml` and `kubernetes/app/07-networkpolicy.yaml`. The act-3 snapshot does not include them.

Compare your work with `act-4-cybersecurity-engineer/` in the `solved` branch.

## Pull the new images

```shell
docker pull semgrep/semgrep
docker pull aquasec/trivy
docker pull ghcr.io/zaproxy/zaproxy:stable
docker pull texlive/texlive
```

Load ZAP into the Minikube node as well. The image is about 1.2 GB and can take several minutes to download. The scan Pod must not spend that time pulling it:

```shell
minikube image load ghcr.io/zaproxy/zaproxy:stable
```

`sqlmap` has no official image. Build it once, then load it into Minikube, the same way you load the app images in Act 3:

```shell
docker compose -f tools/compose.yaml build sqlmap
minikube image load tools-sqlmap:local
```

## Reach the backend directly (episodes 20 to 21)

Keep this running in its own terminal, for the manual `curl` commands only. It is the same pattern Episode 18 used for Prometheus.

```shell
minikube kubectl -- port-forward service/backend -n app 8000:8000
```

`sqlmap` and ZAP do not use this port-forward. Both run as Pods inside the cluster. `sqlmap` reaches the backend at `backend.app.svc.cluster.local:8000`, the same Service name Prometheus already scrapes. ZAP reaches the frontend at `frontend.app.svc.cluster.local:80`, because the checks in Episode 23 are response headers, and those come from Nginx.

## Think like an attacker (episode 20)

Write a one-page scope before you touch the app: the target (`http://localhost:8000`, your own Minikube cluster), what is in scope (the API, the frontend), what is out of scope (anyone else's systems), and when you will stop.

Read the API by hand:

```shell
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
curl http://localhost:8000/api/tasks
curl "http://localhost:8000/api/tasks/search?q=groceries"
```

Burp Suite Community Edition is a GUI intercepting proxy. It cannot run headless in a container for this interactive step, so install it on the host, the same way you installed VS Code and Docker Desktop in Episode 1. Point your browser's proxy at Burp, browse the frontend, and build a site map of every request the app makes.

## Exploit the SQL injection (episode 21)

The search endpoint builds SQL with an f-string:

```python
tasks = connection.execute(
    f"SELECT id, title, done FROM tasks WHERE title LIKE '%{term}%' ORDER BY id DESC"
).fetchall()
```

### Confirm it by hand

A normal search:

```shell
curl -G http://localhost:8000/api/tasks/search --data-urlencode "q=groceries"
```

Break the query with a single quote. The app's global error handler turns the resulting database error into a 503, which is itself a signal: a normal, unmatched search returns `200` with an empty list, not `503`.

```shell
curl -i -G http://localhost:8000/api/tasks/search --data-urlencode "q=groceries'"
```

Confirm it with a boolean payload that closes the quoted string and adds a condition that is always true:

```shell
curl -G http://localhost:8000/api/tasks/search --data-urlencode "q=nonexistent' OR '1'='1' --"
```

Expected: every task comes back, not zero. The search term never matched; the injected condition did.

Extract data with a `UNION` payload. The query selects three columns, so the injected `SELECT` must return three values of compatible types:

```shell
curl -G http://localhost:8000/api/tasks/search --data-urlencode "q=nonexistent' UNION SELECT 1, version(), true --"
```

Expected: one task comes back whose `title` is the PostgreSQL version string, not a task you created.

### Automate it with sqlmap

Run `sqlmap` as a Pod in the `app` namespace, targeting the backend's Service name directly:

```shell
minikube kubectl -- run sqlmap-scan -n app --image=tools-sqlmap:local --image-pull-policy=Never --labels=app.kubernetes.io/name=scanner --restart=Never -- \
  -u "http://backend.app.svc.cluster.local:8000/api/tasks/search?q=test" --batch --level=2 --risk=1
minikube kubectl -- logs sqlmap-scan -n app
minikube kubectl -- delete pod sqlmap-scan -n app
```

Expected: `sqlmap` reports the `q` parameter is injectable: boolean-based blind, stacked queries, time-based blind, and UNION query.

PostgreSQL has no separate "databases" the way MySQL does from one connection. `sqlmap --dbs` lists schemas instead, and the app's tables live in the default `public` schema. List the `tasks` table, then dump it, giving each Pod a new name:

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

Write your findings in a short pentest note: the endpoint, the payload, and what it proved.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `curl` hangs | The port-forward in its own terminal stopped | Restart it |
| `sqlmap` Pod stuck `ImagePullBackOff` | Image not loaded into this cluster, or `--image-pull-policy=Never` missing | Run `minikube image load tools-sqlmap:local` again |
| `sqlmap -D tasks` finds no tables | PostgreSQL lists schemas, not databases, for `--dbs`. The table lives in `public`, not a database named `tasks` | Use `-D public` |
| The UNION payload returns nothing | Column count or type does not match (`id`, `title`, `done`) | Match three columns: an integer, a string, a boolean |

## Fix and harden (episode 22)

### Fix the query

Replace the f-string with a parameterized query, the same pattern every other endpoint in this backend already uses:

```python
tasks = connection.execute(
    "SELECT id, title, done FROM tasks WHERE title LIKE %s ORDER BY id DESC",
    (f"%{term}%",),
).fetchall()
```

Rebuild the backend image. Load the image into Minikube. Restart the Deployment:

```shell
docker build -t tutorial-backend:local ./backend
minikube image load tutorial-backend:local
minikube kubectl -- rollout restart deployment/backend -n app
minikube kubectl -- rollout status deployment/backend -n app
```

Wait for the rollout to finish. Re-run the boolean and UNION `curl` commands from Episode 21. Both must return an empty list. Re-run the `sqlmap` Pod from Episode 21 against the same URL. `sqlmap` must report that the parameter is not injectable. Do not run `sqlmap` through Compose against `host.docker.internal`. `kubectl port-forward` listens on `127.0.0.1` only.

### NetworkPolicies

`kubernetes/app/07-networkpolicy.yaml` already has the default-deny policy for all ingress and egress in `app`. It also has the DNS egress allow rule for `kube-dns` on UDP and TCP port 53. Internal lookups keep working. It also has the `scanner` egress rule for the `sqlmap` and ZAP Pods. Add these allow rules to the same file:

- The frontend accepts ingress on port 80 from anywhere.
- The frontend sends egress to the backend on port 8000.
- The backend accepts ingress on port 8000 from the frontend Pods and the scanner Pods.
- The backend sends egress to the database on port 5432.
- The database accepts ingress on port 5432 from the backend Pods only.
- The `monitoring` namespace accepts ingress to the exporters: frontend port 9113, backend port 8000, and database port 9187.

The default-deny policy blocks egress too. A rule on the destination alone is not enough. Add the egress rule on the source Pod as well.

Use the labels in the manifests: `app.kubernetes.io/name: frontend`, `app.kubernetes.io/name: backend`, and `app.kubernetes.io/name: postgres`. A label such as `app: frontend` matches no Pod.

### Verify on a second profile

Run the probe in the cluster that already runs the app. The probe Pod has no allow rule. The default-deny policy blocks its egress:

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

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Frontend cannot reach backend after the NetworkPolicies | No explicit allow rule between them | Add a policy that allows the frontend's labels to reach the backend's port |
| DNS lookups fail inside Pods | Default-deny also blocked `kube-dns` | Add an egress allow rule for UDP/TCP 53 to the `kube-system` namespace |

## Scan and verify (episode 23)

### SAST: Semgrep

Write a rule in `tools/semgrep/sql-injection.yml` that flags an f-string passed to `.execute(`. Run it against the backend:

```shell
docker compose -f tools/compose.yaml run --rm semgrep \
  semgrep scan --config tools/semgrep/sql-injection.yml backend/
```

Expected: no findings on the fixed code. Temporarily reintroduce the f-string and run it again. Expected: Semgrep flags the line. Revert the change.

### SCA, IaC, and secrets: Trivy

The `trivy` service mounts your Docker socket, so it can inspect a local image by name without a registry. Build the backend image first; the Act 3 guide builds it, but the episodes do not:

```shell
docker build -t tutorial-backend:local ./backend

docker compose -f tools/compose.yaml run --rm trivy image tutorial-backend:local
docker compose -f tools/compose.yaml run --rm trivy config kubernetes/
docker compose -f tools/compose.yaml run --rm trivy fs --scanners secret .
```

Record any findings you do not fix. Not every finding needs a fix today; note why.

### DAST: OWASP ZAP

Run ZAP as a Pod in the `app` namespace too, the same reasoning as `sqlmap`: it reaches the app by Service name, with nothing exposed beyond the cluster.

The baseline scan is passive. It crawls the pages it can reach and checks response headers and cookies. It does not send injection payloads, so it cannot prove the SQL injection fix. `sqlmap` proved that in Episode 21, and Semgrep now guards the pattern in source code. ZAP adds the HTTP layer around it: the headers Nginx returns to every browser.

Target the frontend. The backend has no page at `/`, and its API responses carry Flask headers, not Nginx headers. A scan of a backend URL says nothing about `frontend/nginx.conf`. The frontend serves the HTML pages, so ZAP has a real site to crawl and the header findings come from the right server.

Load the rules file as a ConfigMap, then run the scan:

```shell
minikube kubectl -- create configmap zap-rules -n app --from-file=rules.tsv=tools/zap/rules.tsv
```

```yaml
# zap-scan-pod.yaml
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

### Write the security workflow

Add `.github/workflows/security.yml`. On every pull request, run Semgrep and Trivy. Use your own rule file, `tools/semgrep/sql-injection.yml`, in the Semgrep job. Semgrep's registry rules may not catch this exact pattern. Keep ZAP as a manual, documented step by default. The solved reference also has an optional DAST job. That job starts the Compose stack on the runner and then runs ZAP.

### Nginx headers

Add these lines to the `server` block in `frontend/nginx.conf`:

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

Re-run the same ZAP Pod.

Expected: the anti-clickjacking, `X-Content-Type-Options`, CSP, Permissions Policy, and version leak findings disappear. One Low finding remains, `Cross-Origin-*-Policy Header Missing or Invalid` (90004). Record it and leave it: those policies need every cross-origin resource to cooperate, and this app loads none. Keep the `base-uri`, `form-action`, and `object-src` CSP fallbacks. Without them ZAP raises `CSP: Failure to Define Directive with No Fallback` (10055).

## Broken access control (episode 24)

Before you start, do four things:

1. Add `bcrypt>=4.2,<5` and `PyJWT>=2.9,<3` to `backend/requirements.txt`.
2. Add `JWT_SECRET` to `.env` and `.env.example`.
3. Reset the database volume. Warning: this deletes all data in your local database. Run `docker compose down -v`. PostgreSQL runs `init.sql` only on an empty data directory.
4. Copy `pentest.html`, `pentest.css`, and `pentest.js` into `frontend/`. Add the three files to the `COPY` line in `frontend/Dockerfile`.

Then add a `users` table, a `tasks.owner_id` column, `POST /api/auth/register` (bcrypt-hashed passwords), and `POST /api/auth/login` (a signed JWT). Require `Authorization: Bearer <token>` on every `/api/tasks*` route. Scope `list`, `create`, and `search` to `owner_id`.

Reproduce the IDOR with two real users and `docker compose up --build`. The blocks use bash. On Windows PowerShell 5.1, use `curl.exe`. Set variables with `$env:ALICE_TOKEN = ...`. Use `python` if `python3` is not on PATH.

```shell
curl -s -XPOST -H 'Content-Type: application/json' -d '{"username":"alice","password":"correct-horse-batt"}' localhost:8080/api/auth/register
curl -s -XPOST -H 'Content-Type: application/json' -d '{"username":"bob","password":"correct-horse-batt"}' localhost:8080/api/auth/register

ALICE_TOKEN=$(curl -s -XPOST -H 'Content-Type: application/json' -d '{"username":"alice","password":"correct-horse-batt"}' localhost:8080/api/auth/login | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")
BOB_TOKEN=$(curl -s -XPOST -H 'Content-Type: application/json' -d '{"username":"bob","password":"correct-horse-batt"}' localhost:8080/api/auth/login | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

TASK=$(curl -s -XPOST -H "Authorization: Bearer $ALICE_TOKEN" -H 'Content-Type: application/json' -d '{"title":"Alice secret plan"}' localhost:8080/api/tasks)
TASK_ID=$(printf '%s' "$TASK" | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")

curl -s -o /dev/null -w "status=%{http_code}\n" -XDELETE -H "Authorization: Bearer $BOB_TOKEN" localhost:8080/api/tasks/$TASK_ID
```

Expected: `status=200`. Bob deleted Alice's task using only his own valid token. Use the task ID from the response. Do not assume the ID is 1.

Fix: filter `UPDATE` and `DELETE` by `id = %s AND owner_id = %s`. Return `404` for a task that exists but belongs to someone else. Do not return `403`. A `403` confirms that the task exists. Create a new task as Alice. Delete it as Bob. Expected: `status=404`. The task survives.

Add `try_files $uri $uri.html $uri/ =404;` to the `location /` block in `frontend/nginx.conf`. Without it, `/pentest` returns `404` and only `/pentest.html` works.

A live, clickable version of the same attack and fix is at `http://localhost:8080/pentest`, served by the same frontend. It must be opened through `docker compose`, not a static-file previewer like VS Code's Live Server, which has no `/api/` proxy and returns `405` for the register and login requests.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Register or login returns `405` | Opened `/pentest` through a static-file previewer instead of `docker compose up` | Use `http://localhost:8080/pentest` with the Compose stack running |
| `DELETE`/`PATCH` still succeeds across users after the fix | The `WHERE` clause checks `id` but not `owner_id` | Add `AND owner_id = %s` to both queries |
| Fix returns `403` instead of `404` | Confirms a task's existence to a caller who does not own it | Return `404` for both "not yours" and "does not exist" |

## Encrypt secrets for Git (episode 25)

Since Episode 13, `app-db` has been created by hand and kept out of Git, because a plain Kubernetes Secret only base64-encodes its value. Episode 25 adds a second one, `app-auth` (the JWT signing key), with the same problem. Sealed Secrets closes this gap. Keep the database username from Episode 13 (`tutorial`) in the sealed Secret. A different username creates a role that PostgreSQL does not have.

Warning: Delete the Secrets that you created by hand. The controller does not overwrite a Secret that it does not manage. The backend Pods fail until you apply the SealedSecrets.

```shell
minikube kubectl -- delete secret app-db app-auth -n app --ignore-not-found
minikube kubectl -- apply -f kubernetes/sealed-secrets/controller.yaml
minikube kubectl -- -n kube-system rollout status deploy/sealed-secrets-controller

minikube kubectl -- get secret -n kube-system \
  -l sealedsecrets.bitnami.com/sealed-secrets-key \
  -o jsonpath='{.items[0].data.tls\.crt}' | base64 -d > kubernetes/sealed-secrets/pub-cert.pem

minikube kubectl -- create secret generic app-db -n app \
  --from-literal=username=tutorial --from-literal=password="$(openssl rand -hex 16)" \
  --dry-run=client -o yaml \
  | docker compose -f tools/compose.yaml run --rm -T kubeseal \
      --cert kubernetes/sealed-secrets/pub-cert.pem --format yaml \
  > kubernetes/app/08-sealed-secrets.yaml

minikube kubectl -- create secret generic app-auth -n app \
  --from-literal=jwt-secret="$(openssl rand -hex 32)" \
  --dry-run=client -o yaml \
  | docker compose -f tools/compose.yaml run --rm -T kubeseal \
      --cert kubernetes/sealed-secrets/pub-cert.pem --format yaml \
  >> kubernetes/app/08-sealed-secrets.yaml

minikube kubectl -- apply -f kubernetes/app/08-sealed-secrets.yaml
minikube kubectl -- get secrets -n app
```

Expected: the controller decrypts both `SealedSecret` objects into ordinary Secrets in `app`. `kubernetes/app/08-sealed-secrets.yaml` is safe to commit. Only the cluster that generated the keypair can unseal it.

The sealed `app-db` uses a new random password. The existing PostgreSQL volume still has the old password. Delete the volume so PostgreSQL initializes with the new password. Warning: this deletes the database data.

```shell
minikube kubectl -- scale statefulset postgres -n app --replicas=0
minikube kubectl -- delete pvc postgres-data-postgres-0 -n app
minikube kubectl -- scale statefulset postgres -n app --replicas=1
```

Wire `JWT_SECRET` into the backend Deployment from `app-auth`, the same way `DB_PASSWORD` already reads from `app-db`. Restart the backend Deployment so it reads the new Secret values:

```shell
minikube kubectl -- rollout restart deployment/backend -n app
minikube kubectl -- rollout status deployment/backend -n app
```

Commit `kubernetes/app/08-sealed-secrets.yaml`; ArgoCD's `app` Application already points at the whole folder.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `kubeseal` tries to reach the cluster | `--cert` was left off | Always pass `--cert kubernetes/sealed-secrets/pub-cert.pem` |
| Plaintext Secret committed by mistake | Confused the `--dry-run=client -o yaml` output with the sealed one | Check for `encryptedData`, not `data`, before `git add` |
| `SealedSecret` will not decrypt on a new cluster | Each cluster has its own keypair | Fetch a fresh `pub-cert.pem` and reseal for the new cluster |
| `SealedSecret` reports `already exists and is not managed by SealedSecret` | The hand-created Secret still exists | Delete the Secret, then apply the `SealedSecret` again |
| Backend cannot connect to PostgreSQL after sealing | The volume has the old password | Delete the PVC and restart PostgreSQL |

## Clean up

```shell
docker compose down -v
minikube delete
```

The first command removes the Compose stack from Episode 24 and its database volume. The second command removes the Minikube cluster.

## Act review

| | |
|---|---|
| Task | A search endpoint built SQL from user input, untested and unfixed, and no part of the app checked who was allowed to change what. |
| What you did | Found and exploited the SQL injection by hand and with `sqlmap`, fixed it with a parameterized query, added NetworkPolicies, checked the result with Semgrep, Trivy, and a ZAP baseline scan, added real users and reproduced and fixed an IDOR, then encrypted two secrets for Git with Sealed Secrets. |
| What you achieved | The app resists the injection, every workload has only the network access it needs, a Pod without an allow rule cannot reach the database, every future commit is checked by the same scans, one user can no longer touch another's data, and every secret this app needs is safe to commit. |
| What comes next | Episode 26: combine every act's skills ledger entries into one CV. |

**Resume after Act 4:** use the headline "Junior Cybersecurity Engineer (Penetration Testing and Application Security)". Add the Act 4 rows of the [skills ledger](../cv/skills-ledger.md) to your CV.
