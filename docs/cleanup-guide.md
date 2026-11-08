# Cleanup guide

Run these steps when you finish the course. Run every command from the repository root. The steps remove the resources that the course created on your laptop and on Google Cloud.

Warning: Step 1 deletes all data in the course database. Step 2 deletes the Minikube cluster and its data. Step 3 deletes the Multipass VM. Step 4 deletes the Google Cloud resources.

Note: Some steps fail if you skipped an optional part. For example, `multipass delete` fails if Multipass is not installed. Continue with the next step.

1. Stop both Compose projects. Delete their containers, networks, volumes, and images:

   ```shell
   docker compose down --rmi all -v
   docker compose -f tools/compose.yaml down --rmi all -v
   ```

2. Delete the Minikube clusters:

   ```shell
   minikube delete
   minikube delete -p act4-check
   ```

3. Delete the Multipass VM:

   ```shell
   multipass delete taskboard --purge
   ```

4. Destroy the Google Cloud resources that Terraform created:

   ```shell
   docker compose -f tools/compose.yaml run --rm terraform destroy -auto-approve
   ```

5. Delete the GKE demo cluster:

   ```shell
   gcloud container clusters delete gke-demo --region us-central1 --quiet
   ```

6. Find disks that the GKE demo left behind:

   Warning: The filter can match disks from other clusters. Check the disk name and zone before you delete it.

   ```shell
   gcloud compute disks list --filter='name~pvc-'
   ```

   Delete each disk that the GKE demo created:

   ```shell
   gcloud compute disks delete DISK_NAME --zone ZONE
   ```

7. Remove the course images:

   ```shell
   docker image rm python:3.12-slim postgres:16-alpine nginx:1.27-alpine
   docker image rm semgrep/semgrep aquasec/trivy ghcr.io/zaproxy/zaproxy:stable texlive/texlive
   docker image rm tutorial-frontend:local tutorial-backend:local tutorial-database:local
   docker image rm tools-sqlmap:local tools-kubeseal:latest tools-ansible:latest
   ```

8. Remove stopped containers and build cache:

   ```shell
   docker system prune -f
   ```

9. Check the result:

   ```shell
   docker ps -a
   docker volume ls
   minikube profile list
   gcloud compute instances list
   gcloud compute disks list
   gcloud container clusters list
   ```

   Each command must show no course resource. Your own containers, volumes, and images can remain.

`docker system prune -f` removes stopped containers, unused networks, dangling images, and build cache. It does not remove named volumes. Step 1 removes the course volume and the images that Compose built. It does not remove tagged images that you built by hand. Step 7 removes the course images.

GHCR images are free for public code and need no action. To delete one, open GitHub Packages, open the package, then choose **Delete this package**.

After cleanup, open the Google Cloud Billing page. It must show no running resources.
