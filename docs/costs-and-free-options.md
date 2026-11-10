# Costs and Free Options

The core course is free. You need a laptop, an internet connection, and a free GitHub account.

## What is free

| Service | Used for | Cost |
|---|---|---|
| Docker Desktop | Containers | Free for personal use and education |
| Multipass | Local VMs | Free |
| Minikube | Local Kubernetes | Free |
| GitHub, GitHub Actions | Code and CI | Free for public repositories |
| GHCR | Container images | Free for public images |

## Google Cloud (Episodes 10 and 19, optional)

Episode 10 repeats the Act 2 VM work on Google Cloud. Episode 19 closes with a demo of the same Kubernetes manifests running on [[gcp/gke|GKE]]. You can watch both without an account; neither is required to finish the course.

To follow along, you need a Google Cloud free trial:

- New accounts get trial credits for 90 days. Check the current amount on the Google Cloud free trial page.
- The trial needs a payment card to verify your identity.
- Google Cloud also has an Always Free tier. It includes one `e2-micro` VM in some US regions.

Follow these rules to avoid charges:

1. Create a budget alert before you create any resource.
2. In Episode 10, create resources only with Terraform, and run `terraform destroy` at the end of each session. In Episode 19's GKE demo, delete the cluster with `gcloud container clusters delete` right after the demo.
3. Check the Billing page after the episode. It must show no running resources.

## If your laptop is too small

Acts 1 and 2 need about 4 GB of free memory. Act 3 and 4 need about 8 GB for Minikube.

If your laptop has less memory:

- Do Acts 1 and 2 on your laptop.
- For Acts 3 and 4, use a GitHub Codespace. Personal accounts get a free monthly quota of Codespaces hours. Check the current quota on GitHub before you start, and stop the Codespace when you finish.
