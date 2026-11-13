# CV Skills Ledger

Mark the skills you practiced after each episode. Each act ends with a resume checkpoint: the CV you can send if you stop there. In Episode 26 you combine all checkpoints into one CV.

You can start at any act. Fill in only the acts you complete.

How to read the tables:

- **Episode** is your proof of knowledge. If an interviewer asks, you can point to the episode where you did it.
- **Proof** is the file or result you keep in your repository.
- **CV section** matches the headings in [`cv/template.tex`](../cv/template.tex).

## Act 1: Software Engineer

**Resume after Act 1:** headline "Junior Software Engineer". Fill in Programming & Scripting, Containers & Orchestration, and CI/CD & Automation.

| Skill | Episode | CV section | Proof | Example bullet |
|---|---|---|---|---|
| Git (branches, commits, merges) | [2](https://docs.alialjaffer.com/four-hats/episodes/ep02-git-and-github/) | CI/CD & Automation | Feature branch with clean commits | Managed changes with feature branches and small, reviewable commits |
| GitHub (fork, pull request, code review) | [2](https://docs.alialjaffer.com/four-hats/episodes/ep02-git-and-github/) | CI/CD & Automation | Merged pull request | Contributed through forks and pull requests on GitHub |
| REST API usage (curl, JSON, status codes) | [3](https://docs.alialjaffer.com/four-hats/episodes/ep03-run-the-app/) | Programming & Scripting | `curl` calls against the API | Tested REST endpoints with curl and read HTTP status codes and JSON responses |
| Container networking | [3](https://docs.alialjaffer.com/four-hats/episodes/ep03-run-the-app/) | Containers & Orchestration | Python and Postgres containers on one Docker network | Connected containers by name on a user-defined Docker network |
| SQL, PostgreSQL | [3](https://docs.alialjaffer.com/four-hats/episodes/ep03-run-the-app/), [4](https://docs.alialjaffer.com/four-hats/episodes/ep04-add-a-feature-with-a-test/) | Programming & Scripting | [`database/init.sql`](../database/init.sql), parameterized queries | Wrote parameterized SQL queries against PostgreSQL |
| Python, Flask | [4](https://docs.alialjaffer.com/four-hats/episodes/ep04-add-a-feature-with-a-test/) | Programming & Scripting | `DELETE /api/tasks/<id>` | Built a REST endpoint in Flask with input validation and correct status codes |
| Unit testing (unittest, mocks) | [4](https://docs.alialjaffer.com/four-hats/episodes/ep04-add-a-feature-with-a-test/) | Programming & Scripting | [`backend/test_app.py`](../backend/test_app.py) passes | Covered API behavior with unit tests that mock the database layer |
| Docker (images, layers, tags) | [5](https://docs.alialjaffer.com/four-hats/episodes/ep05-containers/) | Containers & Orchestration | Three Dockerfiles | Containerized a three-tier app (Nginx, Flask, PostgreSQL) with non-root images |
| Docker Compose | [5](https://docs.alialjaffer.com/four-hats/episodes/ep05-containers/) | Containers & Orchestration | `compose.yaml` | Defined a multi-service stack with health checks and startup order in Docker Compose |
| Continuous integration (GitHub Actions) | [6](https://docs.alialjaffer.com/four-hats/episodes/ep06-continuous-integration/) | CI/CD & Automation | `.github/workflows/ci.yml` | Built a CI pipeline in GitHub Actions that tests and builds every pull request |

## Act 2: Cloud Engineer

**Resume after Act 2:** headline "Junior Software Engineer with Cloud and Infrastructure as Code skills". Fill in Cloud Platforms, Infrastructure as Code, Networking & Security, and Operating Systems.

| Skill | Episode | CV section | Proof | Example bullet |
|---|---|---|---|---|
| Cloud service models (IaaS, PaaS, SaaS), regions and zones | [7](https://docs.alialjaffer.com/four-hats/episodes/ep07-plan-the-infrastructure/) | Cloud Platforms | Cloud vocabulary section of the infrastructure plan | Classified cloud services as IaaS, PaaS, or SaaS and chose a region and zone for a workload |
| Capacity planning (CPU, memory, disk) | [7](https://docs.alialjaffer.com/four-hats/episodes/ep07-plan-the-infrastructure/) | Cloud Platforms | Sizing table from `docker stats` | Sized a three-tier app from measured memory use before choosing a VM type |
| Cloud cost estimation | [7](https://docs.alialjaffer.com/four-hats/episodes/ep07-plan-the-infrastructure/) | Cloud Platforms | GCP pricing calculator estimate | Estimated the monthly cost of a VM with the GCP pricing calculator |
| Network planning (VPC, subnets, firewall rules, private versus public services) | [7](https://docs.alialjaffer.com/four-hats/episodes/ep07-plan-the-infrastructure/) | Networking & Security | Network section of the infrastructure plan, port and firewall table | Planned a VPC with one subnet and firewall rules by CIDR range, and kept the database private |
| CIDR notation and subnetting (`/8`, `/16`, `/24`, `/32`) | [7](https://docs.alialjaffer.com/four-hats/episodes/ep07-plan-the-infrastructure/), [10](https://docs.alialjaffer.com/four-hats/episodes/ep10-now-in-the-cloud/) | Networking & Security | CIDR ranges in the plan, `/32` source range in `terraform.tfvars` | Calculated address ranges in CIDR notation and restricted access by source IP range |
| Private address ranges (RFC1918), public versus private IP | [7](https://docs.alialjaffer.com/four-hats/episodes/ep07-plan-the-infrastructure/) | Networking & Security | VPC range in the plan comes from `10.0.0.0/8` | Planned a VPC in a private RFC1918 range and kept public IPs for the web tier only |
| DNS (`nslookup`) | [7](https://docs.alialjaffer.com/four-hats/episodes/ep07-plan-the-infrastructure/) | Networking & Security | `nslookup github.com` output | Traced a DNS name to its public IP address with `nslookup` |
| Architecture diagramming | [7](https://docs.alialjaffer.com/four-hats/episodes/ep07-plan-the-infrastructure/) | Cloud Platforms | Infrastructure diagram | Drew an architecture diagram of the internet, firewall, VM, and containers for team review |
| Virtualization (Multipass) | [8](https://docs.alialjaffer.com/four-hats/episodes/ep08-your-first-vm/) | Operating Systems | Running Ubuntu VM | Provisioned Ubuntu VMs on a hypervisor |
| cloud-init | [8](https://docs.alialjaffer.com/four-hats/episodes/ep08-your-first-vm/) | Infrastructure as Code | `infra/cloud-init/vm.yaml` | Automated first-boot VM setup with cloud-init |
| Linux file permissions (`chmod`) | [8](https://docs.alialjaffer.com/four-hats/episodes/ep08-your-first-vm/) | Operating Systems | `ls -l` output before and after `chmod` | Set file permissions with `chmod` and explained why SSH rejects an open private key |
| Shell (pipes, redirection, environment variables) | [8](https://docs.alialjaffer.com/four-hats/episodes/ep08-your-first-vm/) | Operating Systems | `report.txt` made with a pipe and a redirect | Combined Linux commands with pipes and redirection and configured programs with environment variables |
| Bash scripting | [8](https://docs.alialjaffer.com/four-hats/episodes/ep08-your-first-vm/) | Programming & Scripting | `report.sh` | Wrote a Bash script that reports host, disk, and memory use |
| SSH and key-based authentication | [8](https://docs.alialjaffer.com/four-hats/episodes/ep08-your-first-vm/) | Operating Systems | ed25519 key pair, key-only login | Set up key-only SSH access and disabled password login |
| Linux administration (users, packages, services) | [8](https://docs.alialjaffer.com/four-hats/episodes/ep08-your-first-vm/), [9](https://docs.alialjaffer.com/four-hats/episodes/ep09-configuration-as-code/) | Operating Systems | Commands run on the VM | Administered Ubuntu servers from the command line |
| Ansible (inventory, playbooks, idempotence) | [9](https://docs.alialjaffer.com/four-hats/episodes/ep09-configuration-as-code/) | Infrastructure as Code | `infra/ansible/playbook.yml`, `changed=0` on the second run | Wrote an idempotent Ansible playbook that installs Docker, sets the firewall, and deploys a Compose stack |
| Host firewall (UFW) | [9](https://docs.alialjaffer.com/four-hats/episodes/ep09-configuration-as-code/) | Networking & Security | UFW rules in the playbook | Closed all ports except SSH and HTTP with UFW |
| Terraform | [10](https://docs.alialjaffer.com/four-hats/episodes/ep10-now-in-the-cloud/) | Infrastructure as Code | [`infra/terraform/gcp/`](../infra/terraform/gcp/) | Created a Compute Engine VM with Terraform and removed it with `terraform destroy` |
| Google Cloud (Compute Engine, VPC firewall rules) | [10](https://docs.alialjaffer.com/four-hats/episodes/ep10-now-in-the-cloud/) | Cloud Platforms | Firewall rule limited to your IP | Opened SSH to a single `/32` address with a GCP firewall rule |
| Cloud cost control | [10](https://docs.alialjaffer.com/four-hats/episodes/ep10-now-in-the-cloud/) | Cloud Platforms | Budget alert, empty project after destroy | Set budget alerts and destroyed resources after use to stay within the free trial |
| Load balancers, reverse proxies, CDNs (concepts) | [10](https://docs.alialjaffer.com/four-hats/episodes/ep10-now-in-the-cloud/) | Cloud Platforms | Diagram of users, a load balancer, and three VMs | Explained how a load balancer, a reverse proxy, and a CDN remove the single point of failure and speed up delivery |

## Act 3: DevOps Engineer

**Resume after Act 3:** headline "Junior DevOps Engineer (Kubernetes, CI/CD, Observability)". Fill in Monitoring & Observability and extend Containers & Orchestration and CI/CD & Automation.

| Skill | Episode | CV section | Proof | Example bullet |
|---|---|---|---|---|
| Local Kubernetes cluster (Minikube) | [11](https://docs.alialjaffer.com/four-hats/episodes/ep11-hello-kubernetes/) | Containers & Orchestration | Running cluster with Calico | Ran a local Kubernetes cluster with a network plugin that enforces policies |
| Desired state and self-healing (control loop) | [11](https://docs.alialjaffer.com/four-hats/episodes/ep11-hello-kubernetes/) | Containers & Orchestration | A Deployment replaces a deleted Pod | Explained the Kubernetes control loop and showed a Deployment replacing a deleted Pod |
| Kubernetes workloads (Namespace, Pod, Deployment) | [11](https://docs.alialjaffer.com/four-hats/episodes/ep11-hello-kubernetes/) | Containers & Orchestration | [`kubernetes/app/`](../kubernetes/app/) manifests | Deployed a three-tier app to Kubernetes with Deployments |
| Labels, annotations, selectors, Services (ClusterIP, NodePort, LoadBalancer) | [12](https://docs.alialjaffer.com/four-hats/episodes/ep12-services-and-troubleshooting/) | Containers & Orchestration | Services reach their Pods | Exposed workloads with ClusterIP and NodePort Services selected by labels, and explained when a LoadBalancer Service replaces them |
| Imperative and declarative `kubectl` (`run`, `create`, `expose`, `scale`, `autoscale`) | [11](https://docs.alialjaffer.com/four-hats/episodes/ep11-hello-kubernetes/), [12](https://docs.alialjaffer.com/four-hats/episodes/ep12-services-and-troubleshooting/), [15](https://docs.alialjaffer.com/four-hats/episodes/ep15-scale/) | Containers & Orchestration | A scratch Deployment and Service made from the command line | Used `kubectl` commands for quick tests and YAML manifests for work kept in Git |
| Kubernetes troubleshooting (`describe`, logs, events) | [12](https://docs.alialjaffer.com/four-hats/episodes/ep12-services-and-troubleshooting/) | Containers & Orchestration | Fixed a broken selector | Debugged failing workloads with `kubectl describe`, logs, and events |
| ConfigMaps and Secrets | [13](https://docs.alialjaffer.com/four-hats/episodes/ep13-configuration/) | Containers & Orchestration | Secret created outside Git | Separated configuration and credentials from images with ConfigMaps and Secrets created outside Git |
| Stateful workloads (StatefulSet, PVC, PV) | [14](https://docs.alialjaffer.com/four-hats/episodes/ep14-state/) | Containers & Orchestration | Data survives a Pod restart | Ran PostgreSQL as a StatefulSet with a dynamically provisioned persistent volume |
| Resource requests, limits, probes | [15](https://docs.alialjaffer.com/four-hats/episodes/ep15-scale/) | Containers & Orchestration | Probes in the Deployments | Set resource requests, limits, and health probes on every workload |
| Autoscaling (HPA, metrics-server) | [15](https://docs.alialjaffer.com/four-hats/episodes/ep15-scale/) | Containers & Orchestration | HPA scaled from 2 to 6 replicas under load | Configured a CPU-based HPA that scaled the API from 2 to 6 replicas under load |
| HPA tuning (scale behavior, stabilization window) | [15](https://docs.alialjaffer.com/four-hats/episodes/ep15-scale/) | Containers & Orchestration | `behavior` block in `05-hpa.yaml` | Tuned HPA scale-up and scale-down policies to control how fast the API reacts to load |
| Load testing | [15](https://docs.alialjaffer.com/four-hats/episodes/ep15-scale/) | Monitoring & Observability | Load generator Deployment | Generated controlled load to prove autoscaling works |
| Container registries (GHCR), multi-arch images | [16](https://docs.alialjaffer.com/four-hats/episodes/ep16-publish-images/) | CI/CD & Automation | Images tagged by commit SHA | Built and published multi-architecture images to GHCR, tagged by commit SHA, with GitHub Actions |
| Release automation without workflow loops | [16](https://docs.alialjaffer.com/four-hats/episodes/ep16-publish-images/) | CI/CD & Automation | `publish.yml` bumps manifest tags | Automated image tag updates in manifests without triggering rebuild loops |
| GitOps (ArgoCD) | [17](https://docs.alialjaffer.com/four-hats/episodes/ep17-gitops/) | CI/CD & Automation | ArgoCD `Application` | Implemented GitOps with ArgoCD so every change reaches the cluster through a Git commit, with automated sync and self-heal |
| Prometheus and exporters | [18](https://docs.alialjaffer.com/four-hats/episodes/ep18-observability/) | Monitoring & Observability | Four targets up | Scraped a Flask API, Nginx, and PostgreSQL with Prometheus and exporters |
| PromQL and Grafana dashboards | [18](https://docs.alialjaffer.com/four-hats/episodes/ep18-observability/) | Monitoring & Observability | Dashboard JSON in the repo | Built a Grafana dashboard from PromQL queries and stored it as code |
| Kustomize | [18](https://docs.alialjaffer.com/four-hats/episodes/ep18-observability/) | Containers & Orchestration | [`observability/kustomization.yaml`](../observability/kustomization.yaml) | Deployed the monitoring stack with Kustomize |
| Alerting (Prometheus rules, Alertmanager) | [19](https://docs.alialjaffer.com/four-hats/episodes/ep19-alerting/) | Monitoring & Observability | Alert reaches Discord | Wrote Prometheus alert rules and routed alerts to Discord with Alertmanager |

## Act 4: Cybersecurity Engineer

**Resume after Act 4:** headline "Junior Cybersecurity Engineer (Penetration Testing and Application Security)". Fill in Networking & Security.

| Skill | Episode | CV section | Proof | Example bullet |
|---|---|---|---|---|
| Rules of engagement, authorized testing | [20](https://docs.alialjaffer.com/four-hats/episodes/ep20-think-like-an-attacker/) | Networking & Security | Written scope for the test | Defined scope and rules of engagement before testing an application |
| OWASP Top 10 | [20](https://docs.alialjaffer.com/four-hats/episodes/ep20-think-like-an-attacker/) | Networking & Security | Top 10 mapped to the app | Mapped the OWASP Top 10 to a three-tier application |
| API reconnaissance (curl) | [20](https://docs.alialjaffer.com/four-hats/episodes/ep20-think-like-an-attacker/) | Networking & Security | Endpoint list from reading the API | Enumerated API endpoints and parameters with curl |
| Attack surface mapping (Burp Suite) | [20](https://docs.alialjaffer.com/four-hats/episodes/ep20-think-like-an-attacker/) | Networking & Security | Burp site map | Mapped an application's attack surface with Burp Suite |
| SQL injection (manual exploitation) | [21](https://docs.alialjaffer.com/four-hats/episodes/ep21-exploit-the-sql-injection/) | Networking & Security | Injection confirmed on `/api/tasks/search` | Confirmed and exploited a SQL injection by hand |
| Automated exploitation (sqlmap) | [21](https://docs.alialjaffer.com/four-hats/episodes/ep21-exploit-the-sql-injection/) | Networking & Security | Data extracted with sqlmap | Automated SQL injection data extraction with sqlmap |
| Secure coding (parameterized queries) | [22](https://docs.alialjaffer.com/four-hats/episodes/ep22-fix-and-harden/) | Programming & Scripting | Fixed query, injection no longer works | Fixed a SQL injection with parameterized queries and verified the fix |
| Network segmentation (NetworkPolicies) | [22](https://docs.alialjaffer.com/four-hats/episodes/ep22-fix-and-harden/) | Networking & Security | A Pod without an allow rule cannot reach the database | Isolated tiers with default-deny NetworkPolicies and explicit allow rules |
| SAST (Semgrep) | [23](https://docs.alialjaffer.com/four-hats/episodes/ep23-scan-and-verify/) | Networking & Security | Semgrep flags the injection pattern | Found a SQL injection pattern in source code with Semgrep |
| SCA, IaC, and secret scanning (Trivy) | [23](https://docs.alialjaffer.com/four-hats/episodes/ep23-scan-and-verify/) | Networking & Security | Trivy report | Scanned images, Dockerfiles, Kubernetes YAML, and Terraform for vulnerabilities, misconfigurations, and secrets |
| DAST (OWASP ZAP) | [23](https://docs.alialjaffer.com/four-hats/episodes/ep23-scan-and-verify/) | Networking & Security | ZAP baseline report | Hardened the Nginx response headers and verified them with an OWASP ZAP baseline scan |
| OWASP A01, Broken Access Control, IDOR | [24](https://docs.alialjaffer.com/four-hats/episodes/ep24-broken-access-control/) | Networking & Security | IDOR reproduced against `DELETE /api/tasks/<id>` | Identified and reproduced an Insecure Direct Object Reference end to end |
| Authentication (bcrypt, JWT) | [24](https://docs.alialjaffer.com/four-hats/episodes/ep24-broken-access-control/) | Programming & Scripting | `/api/auth/register`, `/api/auth/login` | Implemented registration and login with bcrypt-hashed passwords and signed JWT bearer tokens |
| Authorization (ownership checks) | [24](https://docs.alialjaffer.com/four-hats/episodes/ep24-broken-access-control/) | Programming & Scripting | `owner_id` check on update and delete, regression test | Added per-object ownership checks that stopped one authenticated user from modifying another's data |
| Secure error design (404 vs. 403) | [24](https://docs.alialjaffer.com/four-hats/episodes/ep24-broken-access-control/) | Networking & Security | 404 returned for another user's task | Chose a response code that fixed an access control bug without creating an object-existence oracle |
| Secrets encryption for GitOps (Sealed Secrets) | [25](https://docs.alialjaffer.com/four-hats/episodes/ep25-encrypt-secrets-for-git/) | Networking & Security | `SealedSecret` manifests committed to Git | Encrypted Kubernetes Secrets with Sealed Secrets so they could be committed to Git and managed by ArgoCD |
| Asymmetric encryption, applied | [25](https://docs.alialjaffer.com/four-hats/episodes/ep25-encrypt-secrets-for-git/) | Networking & Security | Public cert used to seal, private key only in-cluster | Explained and used a public/private keypair where only the cluster could decrypt |

## Cross-cutting skills

These come from working through the whole project. Add them once.

| Skill | Episodes | CV section | Example bullet |
|---|---|---|---|
| Docker-based tooling (no host installs) | [1](https://docs.alialjaffer.com/four-hats/episodes/ep01-set-up-your-laptop/), [9](https://docs.alialjaffer.com/four-hats/episodes/ep09-configuration-as-code/), [10](https://docs.alialjaffer.com/four-hats/episodes/ep10-now-in-the-cloud/) | Containers & Orchestration | Ran Ansible, Terraform, and scanners as containers for a reproducible toolchain |
| Windows and macOS cross-platform setup | [1](https://docs.alialjaffer.com/four-hats/episodes/ep01-set-up-your-laptop/) | Operating Systems | Set up the same toolchain on macOS and Windows |
| Technical documentation | [7](https://docs.alialjaffer.com/four-hats/episodes/ep07-plan-the-infrastructure/), [26](https://docs.alialjaffer.com/four-hats/episodes/ep26-build-your-cv/) | Programming & Scripting | Documented architecture, runbooks, and trade-offs for a multi-tier system |

## How to write a bullet

Use this form: **I did X, using Y, which resulted in Z.**

- X: what you built or changed.
- Y: the tools and methods.
- Z: the result. Use a number when you can, for example "build time fell from 3 minutes to 40 seconds".
