# Act 3: DevOps Engineer (Episodes 11 to 19)

## Your assignment

| | |
|---|---|
| Role | New DevOps Engineer |
| Previously | The software team delivered tested container images. The cloud team ran them on one VM with Ansible and Terraform. That VM has one point of failure, scales by hand, and updates by playbook run. |
| Task | Move the app from one VM to Kubernetes. Make delivery and monitoring automatic. |
| Goal | Deploy to Minikube, scale on load, publish images from CI, deliver changes with Git, and alert on failures. |
| Done when | The app scales from 2 to 6 replicas under load. ArgoCD syncs it from Git. Grafana shows a dashboard. Discord receives an alert. |
| Start here | Fork the starter repository. Copy the contents of `act-2-cloud-engineer/` from the `solved` branch to the root of your fork, not the folder itself. Replace files that have the same name. Do not replace the starter `tools/` and `observability/` folders. Install Docker Desktop and Minikube. You do not need Multipass or GCP. |

Try each task first. Open **Show solution** for that task only when you are stuck. The last line in each solution links to the `solved` branch. Use that link as a last resort.

## What a DevOps Engineer does

A DevOps Engineer connects building software to running it. In a team, you:

- Package the app so it runs the same everywhere.
- Deploy it to a cluster and keep it running.
- Automate the path from a commit to production.
- Watch the system and alert the team when it breaks.
- Scale the app when load grows.

Job titles: DevOps Engineer, Platform Engineer, Site Reliability Engineer (SRE).

## What you build

You deploy the task board from Acts 1 and 2 to Kubernetes on Minikube. Then you add GitOps and monitoring.

| Episode | Topic | Focus | What you do |
|---|---|---|---|
| 11 | Hello, Kubernetes | Platform Engineer | Start Minikube with Calico. Create a Namespace, a Pod, then a Deployment |
| 12 | Services and troubleshooting | Platform Engineer | Add labels and Services. Debug with `describe`, `logs`, and events |
| 13 | Configuration | Platform Engineer | Add a ConfigMap and a Secret |
| 14 | State | Platform Engineer | Run PostgreSQL as a StatefulSet with a PVC |
| 15 | Scale | Site Reliability Engineer (SRE) | Add requests, limits, probes, and an HPA. Run the load generator |
| 16 | Publish images | Release Engineer | Build multi-arch images to GHCR with a workflow |
| 17 | GitOps | DevOps Engineer | Install ArgoCD. Sync the app from Git |
| 18 | Observability | Site Reliability Engineer (SRE) | Add Prometheus scrape targets and a Grafana dashboard |
| 19 | Alerting | Site Reliability Engineer (SRE) | Add an alert rule and a Discord receiver. Closes with a demo-only segment: the same manifests on real GKE |

## What the starter gives you

| Path | Content |
|---|---|
| `observability/namespace.yaml` | The `monitoring` Namespace |
| `observability/prometheus.yaml` | Prometheus Deployment, Service, and a base ConfigMap with only a self-scrape target and empty rules |
| `observability/grafana.yaml` | Grafana Deployment, Service, data source, and dashboard provider |
| `observability/grafana-dashboard.json` | The task board dashboard |
| `observability/alertmanager.yaml` | Alertmanager Deployment and Service with a placeholder receiver |
| `observability/load-generator.yaml` | A load generator at zero replicas |
| `observability/kustomization.yaml` | Builds the files above with Kustomize |

You write everything else: the `kubernetes/app/` manifests, the scrape targets, the alert rule, the Discord receiver, the ArgoCD Applications, and the publish workflow.

Compare your work with `act-3-devops-engineer/` in the `solved` branch.

## Start Minikube

Docker Desktop must run in Linux-container mode. On Windows, use PowerShell, not WSL.

#### Task 1: Start the cluster

Start Minikube with Calico and enable the metrics server.

<details>
<summary>Show solution</summary>

```shell
minikube start --driver=docker --cni=calico --cpus=6 --memory=6144
minikube addons enable metrics-server
```

Calico enforces NetworkPolicies in Act 4. The default CNI does not.

Last resort: [open the solved Act 3 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-3-devops-engineer)

</details>

## Create a GitHub classic PAT to pull from GHCR

Do this section if your fork or its images are private. Minikube cannot pull private images from GHCR without credentials. Public images need no token.

Do this section after you apply the app manifests in the next section. The `app` namespace and the default ServiceAccount must exist first.

A fine-grained token cannot read GHCR packages. Use a classic token.

1. Open GitHub. Go to **Settings > Developer settings > Personal access tokens > Tokens (classic)**.
2. Select **Generate new token (classic)**.
3. Enter the note `ghcr-pull`.
4. Set a short expiry, for example 30 days.
5. Select only the scope `read:packages`.
6. Select **Generate token**.
7. Copy the token now. GitHub shows it once.

Save the token in an environment variable. Never commit it. Replace `YOUR_USERNAME` and `YOUR_TOKEN` with your values.

macOS (bash or zsh):

```shell
export GHCR_USER=YOUR_USERNAME
export GHCR_PAT=YOUR_TOKEN
```

Windows (PowerShell):

```powershell
$env:GHCR_USER = "YOUR_USERNAME"
$env:GHCR_PAT = "YOUR_TOKEN"
```

Create the pull Secret in the `app` namespace:

```shell
minikube kubectl -- create secret docker-registry ghcr-pull -n app --docker-server=ghcr.io --docker-username=$GHCR_USER --docker-password=$GHCR_PAT --dry-run=client -o yaml | minikube kubectl -- apply -f -
```

On PowerShell, write `$env:GHCR_USER` and `$env:GHCR_PAT` in the command.

Attach the Secret to the default ServiceAccount, so every Pod in `app` uses it:

```shell
minikube kubectl -- patch serviceaccount default -n app -p '{"imagePullSecrets":[{"name":"ghcr-pull"}]}'
```

Delete the Pods that failed to pull:

```shell
minikube kubectl -- delete pod --all -n app
```

Check that the Pods start:

```shell
minikube kubectl -- get pods -n app
```

Expected: all Pods reach `Running`.

### Test the token on its own

```shell
echo $GHCR_PAT | docker login ghcr.io -u $GHCR_USER --password-stdin
```

On PowerShell, use `$env:GHCR_PAT` and `$env:GHCR_USER`.

Expected: `Login Succeeded`.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `ImagePullBackOff`, `unauthorized` | Token lacks `read:packages` | Create a new token with that scope |
| `ImagePullBackOff`, `denied` | Token owner cannot see the package | Use the account that owns or can read the repository |
| Secret exists but Pods still fail | Secret is in another namespace | Create it in `app` |
| Pods worked, then failed | Token expired | Create a new token and recreate the Secret |

### Warnings

- Never put the token in a manifest or in Git. ArgoCD syncs only Git, so create this Secret on the command line.
- A classic token reaches every repository you can read. Keep the scope at `read:packages` and revoke the token after the course.
- Making the repository and packages public removes the need for this token.

## Write the app manifests (episodes 11 to 15)

Put the files in `kubernetes/app/`. Apply them in the `app` namespace.

Warning: Do not apply `kubernetes/app/07-networkpolicy.yaml` in Act 3. That file adds a default-deny policy. Act 4 adds the allow rules that the app needs.

#### Task 2: Write the Namespace

Create `kubernetes/app/namespace.yaml` for the `app` Namespace.

<details>
<summary>Show solution</summary>

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: app
  labels:
    app.kubernetes.io/part-of: task-board
```

Last resort: [open the solved namespace.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-3-devops-engineer/kubernetes/app/namespace.yaml)

</details>

#### Task 3: Write the ConfigMap

Create `kubernetes/app/01-configmap.yaml` with `DB_HOST`, `DB_PORT`, `DB_NAME`, and `POSTGRES_DB`.

<details>
<summary>Show solution</summary>

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DB_HOST: postgres
  DB_PORT: "5432"
  DB_NAME: tasks
  POSTGRES_DB: tasks
```

Last resort: [open the solved 01-configmap.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-3-devops-engineer/kubernetes/app/01-configmap.yaml)

</details>

#### Task 4: Write the Services

Create `kubernetes/app/02-services.yaml` with `frontend` (NodePort 30080), `backend`, and a headless `postgres` Service. Include the exporter ports.

<details>
<summary>Show solution</summary>

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
  labels:
    app.kubernetes.io/name: frontend
    app.kubernetes.io/part-of: task-board
spec:
  type: NodePort
  selector:
    app.kubernetes.io/name: frontend
  ports:
    - name: http
      port: 80
      targetPort: http
      nodePort: 30080
    - name: metrics
      port: 9113
      targetPort: metrics
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  labels:
    app.kubernetes.io/name: backend
    app.kubernetes.io/part-of: task-board
spec:
  selector:
    app.kubernetes.io/name: backend
  ports:
    - name: http
      port: 8000
      targetPort: http
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  labels:
    app.kubernetes.io/name: postgres
    app.kubernetes.io/part-of: task-board
spec:
  clusterIP: None
  selector:
    app.kubernetes.io/name: postgres
  ports:
    - name: postgres
      port: 5432
      targetPort: postgres
    - name: metrics
      port: 9187
      targetPort: metrics
```

Last resort: [open the solved 02-services.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-3-devops-engineer/kubernetes/app/02-services.yaml)

</details>

#### Task 5: Write the PostgreSQL StatefulSet

Create `kubernetes/app/03-postgres.yaml` with a `volumeClaimTemplates` entry and a `postgres_exporter` sidecar. Use the `tutorial-database:local` image. Only your built image has `init.sql` baked in, so only it creates the `tasks` table.

<details>
<summary>Show solution</summary>

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  labels:
    app.kubernetes.io/name: postgres
    app.kubernetes.io/part-of: task-board
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: postgres
  template:
    metadata:
      labels:
        app.kubernetes.io/name: postgres
        app.kubernetes.io/part-of: task-board
    spec:
      containers:
        - name: postgres
          image: tutorial-database:local
          imagePullPolicy: IfNotPresent
          ports:
            - name: postgres
              containerPort: 5432
          env:
            - name: POSTGRES_DB
              valueFrom:
                configMapKeyRef:
                  name: app-config
                  key: POSTGRES_DB
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: app-db
                  key: username
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: app-db
                  key: password
            - name: PGDATA
              value: /var/lib/postgresql/data/pgdata
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 1000m
              memory: 1Gi
          startupProbe:
            exec:
              command: ["sh", "-c", "pg_isready -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\""]
            periodSeconds: 5
            failureThreshold: 30
          readinessProbe:
            exec:
              command: ["sh", "-c", "pg_isready -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\""]
            periodSeconds: 5
          livenessProbe:
            exec:
              command: ["sh", "-c", "pg_isready -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\""]
            periodSeconds: 10
          volumeMounts:
            - name: postgres-data
              mountPath: /var/lib/postgresql/data
        - name: postgres-exporter
          image: quay.io/prometheuscommunity/postgres-exporter:v0.17.1
          env:
            - name: DATA_SOURCE_URI
              value: 127.0.0.1:5432/tasks?sslmode=disable
            - name: DATA_SOURCE_USER
              valueFrom:
                secretKeyRef:
                  name: app-db
                  key: username
            - name: DATA_SOURCE_PASS
              valueFrom:
                secretKeyRef:
                  name: app-db
                  key: password
          ports:
            - name: metrics
              containerPort: 9187
          resources:
            requests:
              cpu: 25m
              memory: 32Mi
            limits:
              cpu: 200m
              memory: 128Mi
          readinessProbe:
            httpGet:
              path: /metrics
              port: metrics
          livenessProbe:
            httpGet:
              path: /metrics
              port: metrics
  volumeClaimTemplates:
    - metadata:
        name: postgres-data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 1Gi
```

Last resort: [open the solved 03-postgres.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-3-devops-engineer/kubernetes/app/03-postgres.yaml)

</details>

#### Task 6: Write the Deployments

Create `kubernetes/app/04-deployments.yaml` with `frontend` (Nginx exporter sidecar) and `backend`.

<details>
<summary>Show solution</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  labels:
    app.kubernetes.io/name: frontend
    app.kubernetes.io/part-of: task-board
spec:
  replicas: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: frontend
  template:
    metadata:
      labels:
        app.kubernetes.io/name: frontend
        app.kubernetes.io/part-of: task-board
    spec:
      containers:
        - name: frontend
          image: tutorial-frontend:local
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 80
          resources:
            requests:
              cpu: 50m
              memory: 32Mi
            limits:
              cpu: 250m
              memory: 128Mi
          readinessProbe:
            httpGet:
              path: /
              port: http
          livenessProbe:
            httpGet:
              path: /
              port: http
        - name: nginx-exporter
          image: nginx/nginx-prometheus-exporter:1.4.2
          args:
            - --nginx.scrape-uri=http://127.0.0.1/nginx_status
          ports:
            - name: metrics
              containerPort: 9113
          resources:
            requests:
              cpu: 10m
              memory: 16Mi
            limits:
              cpu: 100m
              memory: 64Mi
          readinessProbe:
            httpGet:
              path: /metrics
              port: metrics
          livenessProbe:
            httpGet:
              path: /metrics
              port: metrics
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  labels:
    app.kubernetes.io/name: backend
    app.kubernetes.io/part-of: task-board
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: backend
  template:
    metadata:
      labels:
        app.kubernetes.io/name: backend
        app.kubernetes.io/part-of: task-board
    spec:
      containers:
        - name: backend
          image: tutorial-backend:local
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8000
          envFrom:
            - configMapRef:
                name: app-config
          env:
            - name: DB_USER
              valueFrom:
                secretKeyRef:
                  name: app-db
                  key: username
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: app-db
                  key: password
          resources:
            requests:
              cpu: 100m
              memory: 96Mi
            limits:
              cpu: 500m
              memory: 256Mi
          readinessProbe:
            httpGet:
              path: /readyz
              port: http
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
            periodSeconds: 10
```

Last resort: [open the solved 04-deployments.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-3-devops-engineer/kubernetes/app/04-deployments.yaml)

</details>

#### Task 7: Write the HPA

Create `kubernetes/app/05-hpa.yaml`. Use backend CPU, 2 to 6 replicas, 50 percent target. Add a `behavior` block with a zero-second stabilization window.

<details>
<summary>Show solution</summary>

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend
  labels:
    app.kubernetes.io/name: backend
    app.kubernetes.io/part-of: task-board
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 6
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      selectPolicy: Max
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
        - type: Pods
          value: 4
          periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 0
      selectPolicy: Max
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 50
```

Last resort: [open the solved 05-hpa.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-3-devops-engineer/kubernetes/app/05-hpa.yaml)

</details>

#### Task 8: Build and load the local images

Before the publish workflow runs, build the images and load them into Minikube. Use the local tags in your manifests.

<details>
<summary>Show solution</summary>

```shell
docker build -t tutorial-frontend:local ./frontend
docker build -t tutorial-backend:local ./backend
docker build -t tutorial-database:local ./database
minikube image load tutorial-frontend:local
minikube image load tutorial-backend:local
minikube image load tutorial-database:local
```

Last resort: [open the solved Act 3 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-3-devops-engineer)

</details>

#### Task 9: Create the namespace and the database Secret

Create the namespace first. Then create the database Secret on the command line. Never commit the Secret. Replace `choose-a-password` with your own password.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- apply -f kubernetes/app/namespace.yaml
minikube kubectl -- create secret generic app-db -n app --from-literal=username=tutorial --from-literal=password=choose-a-password --dry-run=client -o yaml | minikube kubectl -- apply -f -
```

Last resort: [open the solved Act 3 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-3-devops-engineer)

</details>

#### Task 10: Apply the manifests

Apply only the manifests that you wrote in Episodes 11 to 15. If your images are private, create the pull Secret from the first section before you apply.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- apply -n app -f kubernetes/app/01-configmap.yaml
minikube kubectl -- apply -n app -f kubernetes/app/02-services.yaml
minikube kubectl -- apply -n app -f kubernetes/app/03-postgres.yaml
minikube kubectl -- apply -n app -f kubernetes/app/04-deployments.yaml
minikube kubectl -- apply -n app -f kubernetes/app/05-hpa.yaml
```

Last resort: [open the solved Act 3 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-3-devops-engineer)

</details>

#### Task 11: Check the result

Check the Pods, Services, PVC, and HPA. Open the app.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- get pods,services,pvc -n app
minikube kubectl -- get pv
minikube kubectl -- get hpa -n app
minikube service frontend -n app --url
```

Keep `minikube service` running in its own terminal. Press Ctrl+C when you finish. If you need a non-blocking check, use `minikube kubectl -- port-forward service/frontend -n app 8080:80` and open `http://localhost:8080`. If port 8080 is in use, use `18080:80` and open `http://localhost:18080`.

Expected: all Pods `Running`, the PVC `Bound`, and the HPA showing a CPU percentage.

Last resort: [open the solved Act 3 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-3-devops-engineer)

</details>

#### Task 12: Try the command line forms

Use the command line for quick tests. Create a scratch Deployment and Service, then delete them. Scale the backend by hand.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- create deployment scratch --image=nginx -n app
minikube kubectl -- expose deployment scratch --port=80 -n app
minikube kubectl -- get deployment,service scratch -n app
minikube kubectl -- delete deployment,service scratch -n app

minikube kubectl -- scale deployment/backend -n app --replicas=4
minikube kubectl -- scale deployment/backend -n app --replicas=2
```

Service types: ClusterIP is internal, NodePort opens a port on the node, and LoadBalancer asks a cloud for a real load balancer. Minikube uses NodePort.

The HPA in `05-hpa.yaml` has a `behavior` block. It sets how fast the HPA scales up and down. `stabilizationWindowSeconds` is the wait before the HPA acts on a lower number. The default scale-down wait is 5 minutes. The block here sets it to 0 so you can watch the change. Use a longer wait in production.

Last resort: [open the solved Act 3 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-3-devops-engineer)

</details>

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `ImagePullBackOff` | Private image or wrong tag | Create the pull Secret or load the local image |
| StatefulSet Pod stays broken after you fix the image | The rollout waits for the broken Pod | Delete the Pod: `kubectl delete pod postgres-0 -n app` |
| HPA shows `<unknown>` | `metrics-server` is not ready, or no CPU requests | Wait one minute and check the Pod `resources.requests` |
| `postgres` Pod restarts | Secret `app-db` missing | Create the Secret, then delete the Pod |

## Publish images (episode 16)

#### Task 13: Write the publish workflow

Copy `act-3-devops-engineer/.github/workflows/publish.yml` from the `solved` branch into your `.github/workflows/`. Change its paths to match your folders.

<details>
<summary>Show solution</summary>

The solved workflow uses an `ACT` variable and the `act-3-devops-engineer/` prefix. Your fork has the app at the repository root. Remove the variable and the prefix. For example:

```yaml
on:
  push:
    branches:
      - main
    paths:
      - backend/**
      - database/**
      - frontend/**
      - .github/workflows/publish.yml
```

Use `context: ./backend`, `context: ./frontend`, and `context: ./database` in the build steps.

The workflow's `sed` commands match on the image name, for example `tutorial-frontend:`. Your manifests already use this name, so the first run rewrites them to the `ghcr.io` form. If you renamed the local images, update the `sed` patterns to match.

The workflow also rewrites `repoURL` in `kubernetes/argocd/applications/*.yaml`. Episode 17 creates those files. If you run the workflow before Episode 17, remove the `repoURL` line from the workflow. Add it back after Episode 17.

Last resort: [open the solved publish workflow](https://github.com/aliAljaffer/four-hats/blob/solved/act-3-devops-engineer/.github/workflows/publish.yml)

</details>

On a push to `main`, the workflow:

1. Runs the tests.
2. Builds `linux/amd64` and `linux/arm64` images.
3. Tags them with the commit SHA and pushes them to GHCR.
4. Writes the new tags into your manifests and commits as `github-actions[bot]`.

The workflow runs only when `backend/`, `database/`, `frontend/`, or the workflow file changes. The bot commit changes only manifests, so it does not start a loop.

## GitOps with ArgoCD (episode 17)

ArgoCD runs in the cluster and pulls from Git. The workflow never connects to your cluster.

#### Task 14: Install ArgoCD

Install ArgoCD in the `argocd` namespace.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- create namespace argocd --dry-run=client -o yaml | minikube kubectl -- apply -f -
minikube kubectl -- apply --server-side --force-conflicts -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v3.5.1/manifests/install.yaml
```

Last resort: [open the solved Act 3 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-3-devops-engineer)

</details>

#### Task 15: Create the Grafana Secret

Create the Secret that ArgoCD cannot read from Git. `app-db` already exists: you created it by hand in [Task 9](#task-9-create-the-namespace-and-the-database-secret), so its password never enters Git. This task creates `grafana-admin` only. Replace `choose-a-password` with your own password.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- apply -f observability/namespace.yaml
minikube kubectl -- create secret generic grafana-admin -n monitoring --from-literal=admin-user=admin --from-literal=admin-password=choose-a-password --dry-run=client -o yaml | minikube kubectl -- apply -f -
```

Last resort: [open the solved Act 3 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-3-devops-engineer)

</details>

#### Task 16: Write the ArgoCD Applications

Write two Applications in `kubernetes/argocd/applications/`: `app.yaml` and `monitoring.yaml`. Each one needs:

- `repoURL`: your fork.
- `path`: `kubernetes/app` or `observability`.
- `destination.namespace`: `app` or `monitoring`.
- `syncPolicy.automated` with `prune: true` and `selfHeal: true`.

<details>
<summary>Show solution</summary>

Create the folder first:

```shell
mkdir -p kubernetes/argocd/applications
```

`kubernetes/argocd/applications/app.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/YOUR_USERNAME/four-hats.git
    targetRevision: main
    path: kubernetes/app
  destination:
    server: https://kubernetes.default.svc
    namespace: app
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

`kubernetes/argocd/applications/monitoring.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: monitoring
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/YOUR_USERNAME/four-hats.git
    targetRevision: main
    path: observability
  destination:
    server: https://kubernetes.default.svc
    namespace: monitoring
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

Apply them:

```shell
minikube kubectl -- apply -f kubernetes/argocd/applications/
```

Warning: ArgoCD needs read access to a private repository. Make the fork public, or add the repository credentials in ArgoCD.

Last resort: [open the solved ArgoCD examples](https://github.com/aliAljaffer/four-hats/tree/solved/act-3-devops-engineer/kubernetes/argocd/applications)

</details>

#### Task 17: Test GitOps

Change `replicas` in a manifest. Commit and push. Watch ArgoCD apply the change.

<details>
<summary>Show solution</summary>

Change `replicas: 3` to `replicas: 1` in `kubernetes/app/04-deployments.yaml`. Commit and push. Watch the frontend Deployment scale down. Change it back to `3`, commit, and push. Watch it scale up.

Last resort: [open the solved 04-deployments.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-3-devops-engineer/kubernetes/app/04-deployments.yaml)

</details>

## Observability (episode 18)

#### Task 18: Add Prometheus scrape targets

Open `observability/prometheus.yaml`. Add scrape jobs to `scrape_configs`.

| Job | Target |
|---|---|
| `backend` | `backend.app.svc.cluster.local:8000` (path `/metrics`) |
| `frontend` | `frontend.app.svc.cluster.local:9113` |
| `postgres` | `postgres.app.svc.cluster.local:9187` |

The `frontend` and `postgres` targets need their exporter's port on the Service, not only the app's own port. Add it to `02-services.yaml` if it is missing.

<details>
<summary>Show solution</summary>

Add these jobs under `scrape_configs` in `observability/prometheus.yaml`:

```yaml
      - job_name: backend
        metrics_path: /metrics
        static_configs:
          - targets:
              - backend.app.svc.cluster.local:8000

      - job_name: frontend
        static_configs:
          - targets:
              - frontend.app.svc.cluster.local:9113

      - job_name: postgres
        static_configs:
          - targets:
              - postgres.app.svc.cluster.local:9187
```

Last resort: [open the solved prometheus.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-3-devops-engineer/observability/prometheus.yaml)

</details>

#### Task 19: Deploy and check Prometheus

Deploy the observability manifests, restart Prometheus, and open the targets page.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- apply -k observability
minikube kubectl -- rollout restart deployment/prometheus -n monitoring
minikube kubectl -- port-forward service/prometheus -n monitoring 9090:9090
```

A ConfigMap change does not restart the Pods that read it. Prometheus only reads `prometheus.yml` once, at startup, so restart it every time you change `scrape_configs` or `rules.yml`.

Open `http://localhost:9090/targets`. Expected: every target is `UP`.

Last resort: [open the solved prometheus.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-3-devops-engineer/observability/prometheus.yaml)

</details>

#### Task 20: Open Grafana

Open Grafana. Log in with the `grafana-admin` Secret.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- port-forward service/grafana -n monitoring 3000:3000
```

Open `http://localhost:3000`. Log in as `admin` with the password from the `grafana-admin` Secret. The dashboard shows request rate, latency, frontend connections, database connections, and requests by endpoint.

Last resort: [open the solved observability folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-3-devops-engineer/observability)

</details>

#### Task 21: Run the load test

Apply the load generator, scale it to six replicas, and watch the HPA. Stop the load when you finish.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- apply -n monitoring -f observability/load-generator.yaml
minikube kubectl -- scale deployment/load-generator -n monitoring --replicas=6
minikube kubectl -- get hpa backend -n app --watch
```

Expected: the backend scales from 2 to 6 replicas. Stop the load:

```shell
minikube kubectl -- scale deployment/load-generator -n monitoring --replicas=0
```

The HPA checks every 15 seconds. CPU metrics can lag, so give it a minute.

Last resort: [open the solved load-generator.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-3-devops-engineer/observability/load-generator.yaml)

</details>

## Alerting (episode 19)

#### Task 22: Create a Discord webhook

In Discord, create a webhook for a channel. Copy the webhook URL. Warning: the webhook URL is a secret. Never commit it.

<details>
<summary>Show solution</summary>

In Discord, open your server. Choose **Server Settings > Integrations > Webhooks**. Select **New Webhook**. Choose a channel. Select **Copy Webhook URL**.

Last resort: [open the solved alertmanager.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-3-devops-engineer/observability/alertmanager.yaml)

</details>

#### Task 23: Create the Alertmanager Secret

Create the Secret that holds the webhook URL. Replace `YOUR_WEBHOOK_URL` with the URL from Discord.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- create secret generic alertmanager-discord -n monitoring --from-literal=webhook_url=YOUR_WEBHOOK_URL --dry-run=client -o yaml | minikube kubectl -- apply -f -
```

Last resort: [open the solved alertmanager.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-3-devops-engineer/observability/alertmanager.yaml)

</details>

#### Task 24: Write the alert rule

In `observability/prometheus.yaml`, replace `groups: []` in `rules.yml` with a `BackendUnavailable` group.

<details>
<summary>Show solution</summary>

```yaml
groups:
  - name: task-board
    rules:
      - alert: BackendUnavailable
        expr: up{job="backend"} == 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: Backend is unavailable
          description: Prometheus cannot scrape the backend.
```

Last resort: [open the solved prometheus.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-3-devops-engineer/observability/prometheus.yaml)

</details>

#### Task 25: Write the Discord receiver

In `observability/alertmanager.yaml`, change `route.receiver` to `discord`, replace the `blackhole` receiver with a `discord_configs` receiver, add a `discord` volume from the Secret `alertmanager-discord`, and mount it at `/etc/alertmanager/secrets/discord`, read-only.

<details>
<summary>Show solution</summary>

The receiver:

```yaml
receivers:
  - name: discord
    discord_configs:
      - webhook_url_file: /etc/alertmanager/secrets/discord/webhook_url
        send_resolved: true
```

The volume:

```yaml
      volumes:
        - name: discord
          secret:
            secretName: alertmanager-discord
```

The mount:

```yaml
          volumeMounts:
            - name: discord
              mountPath: /etc/alertmanager/secrets/discord
              readOnly: true
```

Restart both after the change:

```shell
minikube kubectl -- rollout restart deployment/prometheus -n monitoring
minikube kubectl -- rollout restart deployment/alertmanager -n monitoring
```

Last resort: [open the solved alertmanager.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-3-devops-engineer/observability/alertmanager.yaml)

</details>

#### Task 26: Trigger an alert

Pause ArgoCD automated sync, scale the backend to zero, wait for the alert, then restore the sync and the replicas.

Warning: ArgoCD's `selfHeal` restores `replicas: 2` within a few seconds, long before the alert's `for: 1m` can be satisfied. Pause automated sync first, or the alert never fires.

<details>
<summary>Show solution</summary>

```shell
minikube kubectl -- patch application app -n argocd --type merge -p '{"spec":{"syncPolicy":{"automated":null}}}'
minikube kubectl -- scale deployment/backend -n app --replicas=0
```

Expected: Discord shows `BackendUnavailable` after about one minute.

Turn automated sync back on:

```shell
minikube kubectl -- patch application app -n argocd --type merge -p '{"spec":{"syncPolicy":{"automated":{"prune":true,"selfHeal":true}}}}'
```

The HPA cannot scale the backend up from zero replicas. Scale the Deployment back to two replicas:

```shell
minikube kubectl -- scale deployment/backend -n app --replicas=2
```

If you did not install ArgoCD, run the same scale command.

Last resort: [open the solved alertmanager.yaml](https://github.com/aliAljaffer/four-hats/blob/solved/act-3-devops-engineer/observability/alertmanager.yaml)

</details>

## Clean up

#### Task 27: Delete the cluster

Delete the cluster.

<details>
<summary>Show solution</summary>

```shell
minikube delete
```

Warning: this deletes the cluster and all PostgreSQL data. Minikube storage is for learning only.

Last resort: [open the solved Act 3 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-3-devops-engineer)

</details>

## Demo: the same app on GKE

This part is a demo, presenter-only. There is nothing for you to do here, and nothing to submit. You can watch it without a Google Cloud account. The presenter needs `gcloud` and `kubectl` on the host machine.

Everything in this act ran on Minikube, a single-node cluster on your laptop. Production Kubernetes is usually managed: GKE, EKS, or AKS run the control plane for you. The manifests you wrote in episodes 11 to 15 do not change.

Warning: this needs a Google Cloud free trial and creates real billable resources. Set a budget alert before creating anything; see [Costs and free options](costs-and-free-options.md).

```shell
gcloud components install kubectl
gcloud components install gke-gcloud-auth-plugin
gcloud container clusters create-auto gke-demo --region us-central1
gcloud container clusters get-credentials gke-demo --region us-central1
```

The demo needs the images that the [Task 13 publish workflow](#task-13-write-the-publish-workflow) pushed to GHCR. GKE pulls images from a registry; it cannot see images on your laptop. Local images from `minikube image load` do not exist on GKE. If you skipped Episode 16, publish the images first or use another registry.

Apply the same `kubernetes/app/` manifests: the Namespace, the Deployments, the Services, the Postgres StatefulSet, the ConfigMaps, and the Secrets. Change the frontend Service from `type: NodePort` to `type: LoadBalancer` for this demo. Change each `image:` value to the published image. Then:

```shell
kubectl get nodes
kubectl get pods -n app
kubectl get svc -n app
```

Same Deployments, StatefulSet, ConfigMaps, and Secrets, running on a different cluster. What changes: a managed control plane, automatic node upgrades, and a `LoadBalancer` Service that gets a real external IP, which Minikube cannot do without MetalLB. A `NodePort` Service never gets an external IP on GKE. What does not change: everything else this act already covered.

```shell
gcloud container clusters delete gke-demo --region us-central1 --quiet
```

The cluster can leave Persistent Disk volumes behind. List the disks:

Warning: The filter can match disks from other clusters. Check the disk name and zone before you delete it.

```shell
gcloud compute disks list --filter='name~pvc-'
```

Delete each disk that the GKE demo created:

```shell
gcloud compute disks delete DISK_NAME --zone ZONE
```

Check the Billing page. It must show no running resources.

## Act review

| | |
|---|---|
| Task | One VM was a single point of failure. Updates, scaling, and monitoring were manual. |
| What you did | Deployed to Kubernetes with state, probes, and autoscaling. Published images from CI. Delivered changes with ArgoCD. Added Prometheus, Grafana, and Alertmanager. |
| What you achieved | The app heals itself, scales under load, receives every commit through Git, and alerts Discord when the backend fails. |
| What comes next | The Cybersecurity Engineer pentests the app and finds a SQL injection (Act 4). |

**Resume after Act 3:** use the headline "Junior DevOps Engineer (Kubernetes, CI/CD, Observability)". Add the Act 3 rows of the [skills ledger](../cv/skills-ledger.md) to your CV.
