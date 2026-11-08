# Four Hats: Four Tech Careers in One Project

You just graduated in Computer Science or a similar major. This course shows you four careers by letting you do the work of each one on a single app. At the end, you have a project on GitHub and a CV full of skills you practiced.

The course is a YouTube series. This repository is the starter code that you fork and build on.

## The four roles

| Act | Role | You will |
|---|---|---|
| 1 | Software Engineer | Add a feature with a test, package the app in containers, add CI |
| 2 | Cloud Engineer | Plan and build VMs with cloud-init, Ansible, and Terraform |
| 3 | DevOps Engineer | Deploy to Kubernetes with GitOps, autoscaling, and monitoring |
| 4 | Cybersecurity Engineer | Pentest the app, exploit and fix a SQL injection, harden and scan it |

## Start at any act

Each act is a separate job. Pick the one you want.

Act guides: [Act 1](docs/act1-software-engineer.md), [Act 2](docs/act2-cloud-engineer.md), [Act 3](docs/act3-devops-engineer.md), [Act 4](docs/act4-cybersecurity-engineer.md).

Each act guide gives you the task first. Open **Show solution** only for the task you are stuck on. The `solved` branch is the last resort.

- Each act opens with a briefing: what happened before, your task, and what "done" means.
- Each act ends with a review and a resume checkpoint: the skills you can now add to your CV.
- To skip ahead, fork the starter repository first. Then copy the previous act's folder from the `solved` branch into your fork. Each act doc says which folder.
- An act folder contains the app at the end of that act. It does not contain the tool services that a later act adds. Keep `tools/` from your fork.
- Everyone needs the Episode 1 setup.

## What it costs

Nothing. Everything runs on your laptop. One optional episode uses a Google Cloud free trial. See [Costs and free options](docs/costs-and-free-options.md). When you finish an act, see the [Cleanup guide](docs/cleanup-guide.md).

## Requirements

- macOS, or Windows 10/11
- 8 GB of memory or more (16 GB is better)
- 30 GB of free disk space
- A free GitHub account

Install steps are in [Setup](docs/00-setup.md).

## Episodes

| Part | Doc |
|---|---|
| Ep 0 to 1: Introduction and setup | [Setup](docs/00-setup.md) |
| Ep 2 to 6: Software Engineer | [Act 1](docs/act1-software-engineer.md) |
| Ep 7 to 10: Cloud Engineer | [Act 2](docs/act2-cloud-engineer.md) |
| Ep 11 to 19: DevOps Engineer | [Act 3](docs/act3-devops-engineer.md) |
| Ep 20 to 25: Cybersecurity Engineer | [Act 4](docs/act4-cybersecurity-engineer.md) |
| Ep 26: Build your CV | [Skills ledger](cv/skills-ledger.md) |


## Stuck?

Each act has a finished version in the `solved` branch of this repository. On GitHub, open the branch menu and select `solved`. Open the folder for your act, for example `act-1-software-engineer/`, and compare it with your work.

Each act folder is a source snapshot. The Act 3 and Act 4 manifests reference GHCR images. Build the images locally or publish your own before you run them.

## Project layout

```text
backend/        Flask API and tests
frontend/       Static UI and Nginx config
database/       PostgreSQL schema
observability/  Prometheus, Grafana, Alertmanager, and dashboard (Act 3)
infra/          Cloud-init, Ansible, and Terraform (Act 2)
tools/          Docker Compose services for course tools
docs/           Act guides
cv/             Skills ledger and CV template
```
