# Act 3: DevOps Engineer (Episodes 11 to 19)

## Your assignment

| | |
|---|---|
| Role | New DevOps Engineer |
| Previously | The software team delivered tested container images. The cloud team ran them on one VM with Ansible and Terraform. That VM has one point of failure, scales by hand, and updates by playbook run. |
| Task | Move the app from one VM to Kubernetes. Make delivery and monitoring automatic. |
| Goal | Deploy to Minikube, scale on load, publish images from CI, deliver changes with Git, and alert on failures. |
| Done when | The app scales from 2 to 6 replicas under load. ArgoCD syncs it from Git. Grafana shows a dashboard. Discord receives an alert. |
| Start here | Fork the starter repository. Copy `act-2-cloud-engineer/` from the `solved` branch into your fork. Keep the starter `tools/` and `observability/` folders. Install Docker Desktop and Minikube. You do not need Multipass or GCP. |

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

```shell
minikube start --driver=docker --cni=calico --cpus=6 --memory=6144
minikube addons enable metrics-server
```

Calico enforces NetworkPolicies in Act 4. The default CNI does not.

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

Save the token in an environment variable. Never commit it.

macOS (bash or zsh):

```shell
export GHCR_USER=<your-github-username>
export GHCR_PAT=<paste-token>
```

Windows (PowerShell):

```powershell
$env:GHCR_USER = "<your-github-username>"
$env:GHCR_PAT = "<paste-token>"
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

| File | Content |
|---|---|
| `namespace.yaml` | Namespace `app` |
| `01-configmap.yaml` | `DB_HOST`, `DB_PORT`, `DB_NAME`, `POSTGRES_DB` |
| `02-services.yaml` | `frontend` (NodePort 30080), `backend`, and a headless `postgres` Service |
| `03-postgres.yaml` | StatefulSet with a `volumeClaimTemplates` entry and a `postgres_exporter` sidecar. Use the `tutorial-database:local` image from the "Run local images first" section above, not the stock `postgres:16-alpine` image: only your built image has `init.sql` baked in, so only it creates the `tasks` table |
| `04-deployments.yaml` | `frontend` with an Nginx exporter sidecar, and `backend` |
| `05-hpa.yaml` | HPA on backend CPU: 2 to 6 replicas, 50% target |

Warning: Do not apply `kubernetes/app/07-networkpolicy.yaml` in Act 3. That file adds a default-deny policy. Act 4 adds the allow rules that the app needs.

### Run local images first

Before the publish workflow runs, build the images and load them into Minikube. Use the local tags in your manifests.

```shell
docker build -t tutorial-frontend:local ./frontend
docker build -t tutorial-backend:local ./backend
docker build -t tutorial-database:local ./database
minikube image load tutorial-frontend:local
minikube image load tutorial-backend:local
minikube image load tutorial-database:local
```

### Create the namespace and the database Secret

Create the namespace first. Then create the database Secret on the command line. Never commit the Secret.

```shell
minikube kubectl -- apply -f kubernetes/app/namespace.yaml
minikube kubectl -- create secret generic app-db -n app --from-literal=username=tutorial --from-literal=password=<choose-a-password> --dry-run=client -o yaml | minikube kubectl -- apply -f -
```

### Apply the manifests

Apply only the manifests that you wrote in Episodes 11 to 15. If your images are private, create the pull Secret from the first section before you apply.

```shell
minikube kubectl -- apply -n app -f kubernetes/app/01-configmap.yaml
minikube kubectl -- apply -n app -f kubernetes/app/02-services.yaml
minikube kubectl -- apply -n app -f kubernetes/app/03-postgres.yaml
minikube kubectl -- apply -n app -f kubernetes/app/04-deployments.yaml
minikube kubectl -- apply -n app -f kubernetes/app/05-hpa.yaml
```

### Try the command line forms

Kubernetes keeps the desired state you declare. A control loop compares what runs with what you asked for and fixes any difference. This is why a Deployment replaces a deleted Pod and a bare Pod does not return.

Use the command line for quick tests. Keep YAML for work you commit.

```shell
minikube kubectl -- create deployment scratch --image=nginx -n app
minikube kubectl -- expose deployment scratch --port=80 -n app
minikube kubectl -- get deployment,service scratch -n app
minikube kubectl -- delete deployment,service scratch -n app
```

Scale the backend by hand. An HPA sets the count back when you apply it.

```shell
minikube kubectl -- scale deployment/backend -n app --replicas=4
minikube kubectl -- scale deployment/backend -n app --replicas=2
```

Service types: ClusterIP is internal, NodePort opens a port on the node, and LoadBalancer asks a cloud for a real load balancer. Minikube uses NodePort.

The HPA in `05-hpa.yaml` has a `behavior` block. It sets how fast the HPA scales up and down. `stabilizationWindowSeconds` is the wait before the HPA acts on a lower number. The default scale-down wait is 5 minutes. The block here sets it to 0 so you can watch the change. Use a longer wait in production.

### Check the result

```shell
minikube kubectl -- get pods,services,pvc -n app
minikube kubectl -- get pv
minikube kubectl -- get hpa -n app
```

Expected: all Pods `Running`, the PVC `Bound`, and the HPA showing a CPU percentage.

Open the app. Keep this command running in its terminal.

```shell
minikube service frontend -n app --url
```

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `ImagePullBackOff` | Private image or wrong tag | Create the pull Secret or load the local image |
| StatefulSet Pod stays broken after you fix the image | The rollout waits for the broken Pod | Delete the Pod: `kubectl delete pod postgres-0 -n app` |
| HPA shows `<unknown>` | `metrics-server` is not ready, or no CPU requests | Wait one minute and check the Pod `resources.requests` |
| `postgres` Pod restarts | Secret `app-db` missing | Create the Secret, then delete the Pod |

## Publish images (episode 16)

Copy `act-3-devops-engineer/.github/workflows/publish.yml` from the `solved` branch into your `.github/workflows/`. Change its paths to match your folders.

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

The workflow's `sed` commands match on the image name, for example `tutorial-frontend:`. Your manifests already use this name from "Run local images first" above, so the first run rewrites them to the `ghcr.io` form. If you renamed the local images, update the `sed` patterns to match.

The workflow also rewrites `repoURL` in `kubernetes/argocd/applications/*.yaml`. Episode 17 creates those files. If you run the workflow before Episode 17, remove the `repoURL` line from the workflow. Add it back after Episode 17.

On a push to `main`, the workflow:

1. Runs the tests.
2. Builds `linux/amd64` and `linux/arm64` images.
3. Tags them with the commit SHA and pushes them to GHCR.
4. Writes the new tags into your manifests and commits as `github-actions[bot]`.

The workflow runs only when `backend/`, `database/`, `frontend/`, or the workflow file changes. The bot commit changes only manifests, so it does not start a loop.

## GitOps with ArgoCD (episode 17)

ArgoCD runs in the cluster and pulls from Git. The workflow never connects to your cluster.

Install ArgoCD:

```shell
minikube kubectl -- create namespace argocd --dry-run=client -o yaml | minikube kubectl -- apply -f -
minikube kubectl -- apply --server-side --force-conflicts -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v3.5.1/manifests/install.yaml
```

Create the Secret that ArgoCD cannot read from Git. `app-db` already exists from Episode 13.

```shell
minikube kubectl -- apply -f observability/namespace.yaml
minikube kubectl -- create secret generic grafana-admin -n monitoring --from-literal=admin-user=admin --from-literal=admin-password=<choose-a-password> --dry-run=client -o yaml | minikube kubectl -- apply -f -
```

Write two Applications in `kubernetes/argocd/applications/`: `app.yaml` and `monitoring.yaml`. Each one needs:

- `repoURL`: your fork.
- `path`: `kubernetes/app` or `observability`.
- `destination.namespace`: `app` or `monitoring`.
- `syncPolicy.automated` with `prune: true` and `selfHeal: true`.

Apply them:

```shell
minikube kubectl -- apply -f kubernetes/argocd/applications/
```

Warning: ArgoCD needs read access to a private repository. Make the fork public, or add the repository credentials in ArgoCD.

Test GitOps. Change `replicas` in a manifest. Commit and push. Watch ArgoCD apply the change.

## Observability (episode 18)

Open `observability/prometheus.yaml`. Add scrape jobs to `scrape_configs`.

| Job | Target |
|---|---|
| `backend` | `backend.app.svc.cluster.local:8000` (path `/metrics`) |
| `frontend` | `frontend.app.svc.cluster.local:9113` |
| `postgres` | `postgres.app.svc.cluster.local:9187` |

The `frontend` and `postgres` targets need their exporter's port on the Service, not only the app's own port. Add it to `02-services.yaml` if it is missing.

Deploy and open Prometheus:

```shell
minikube kubectl -- apply -k observability
minikube kubectl -- rollout restart deployment/prometheus -n monitoring
minikube kubectl -- port-forward service/prometheus -n monitoring 9090:9090
```

A ConfigMap change does not restart the Pods that read it. Prometheus only reads `prometheus.yml` once, at startup, so restart it every time you change `scrape_configs` or `rules.yml`.

Open `http://localhost:9090/targets`. Expected: every target is `UP`.

Open Grafana. Log in with the `grafana-admin` Secret.

```shell
minikube kubectl -- port-forward service/grafana -n monitoring 3000:3000
```

Open `http://localhost:3000`. The dashboard shows request rate, latency, frontend connections, and database connections.

### Load test

```shell
minikube kubectl -- apply -n monitoring -f observability/load-generator.yaml
minikube kubectl -- scale deployment/load-generator -n monitoring --replicas=6
minikube kubectl -- get hpa backend -n app --watch
```

Expected: the backend scales from 2 to 6 replicas. Stop the load when you finish.

```shell
minikube kubectl -- scale deployment/load-generator -n monitoring --replicas=0
```

The HPA checks every 15 seconds. CPU metrics can lag, so give it a minute.

## Alerting (episode 19)

### Create a Discord webhook

1. In Discord, open your server. Choose **Server Settings > Integrations > Webhooks**.
2. Select **New Webhook**. Choose a channel.
3. Select **Copy Webhook URL**.

Warning: the webhook URL is a secret. Never commit it.

Create the Secret:

```shell
minikube kubectl -- create secret generic alertmanager-discord -n monitoring --from-literal=webhook_url=<your-webhook-url> --dry-run=client -o yaml | minikube kubectl -- apply -f -
```

### Write the alert rule

In `observability/prometheus.yaml`, replace `groups: []` in `rules.yml` with this group:

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

### Write the Discord receiver

In `observability/alertmanager.yaml`:

1. Change `route.receiver` to `discord`.
2. Replace the `blackhole` receiver with this one.

```yaml
receivers:
  - name: discord
    discord_configs:
      - webhook_url_file: /etc/alertmanager/secrets/discord/webhook_url
        send_resolved: true
```

3. Add a `discord` volume from the Secret `alertmanager-discord`.
4. Mount it at `/etc/alertmanager/secrets/discord`, read-only.

Alertmanager and the Prometheus rule file also load once at startup. After this change syncs, restart both:

```shell
minikube kubectl -- rollout restart deployment/prometheus -n monitoring
minikube kubectl -- rollout restart deployment/alertmanager -n monitoring
```

### Trigger an alert

Warning: ArgoCD's `selfHeal` restores `replicas: 2` within a few seconds, long before the alert's `for: 1m` can be satisfied. Pause automated sync on the `app` Application first, or the alert never fires.

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

## Clean up

```shell
minikube delete
```

Warning: this deletes the cluster and all PostgreSQL data. Minikube storage is for learning only.

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

The demo needs the images that Episode 16 published to GHCR. Local images from `minikube image load` do not exist on GKE. If you skipped Episode 16, publish the images first or use another registry.

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
gcloud compute disks delete <disk-name> --zone <zone>
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
