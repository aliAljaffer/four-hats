# Act 2: Cloud Engineer (Episodes 7 to 10)

## Your assignment

| | |
|---|---|
| Role | New Cloud Engineer |
| Previously | The software team added a tested delete feature, containers, Compose, and CI. |
| Task | The app runs only on developer laptops. Nobody else can reach it. |
| Goal | Run the app on a server that users can reach. Build the server from code. Keep cost known and open ports few. |
| Done when | cloud-init and Ansible build a VM that runs the app. Terraform builds the same on Google Cloud. You destroy it afterwards. |
| Start here | Fork the starter repository. Copy `act-1-software-engineer/` from the `solved` branch into your fork. Keep the starter `tools/` folder. Install Docker Desktop and Multipass. |

## What a Cloud Engineer does

A Cloud Engineer builds and runs the infrastructure that applications need. In a team, you:

- Plan the size, network, and cost of the infrastructure before you build it.
- Create servers, networks, and firewalls.
- Write the setup as code, so anyone can repeat it.
- Control cost.
- Keep the servers patched and reachable.

Job titles: Cloud Engineer, Infrastructure Engineer, Systems Engineer, Site Reliability Engineer (SRE).

## What you build

One virtual machine (VM) runs the task board from Act 1. You build it three ways:

| Episode | Tool | Focus | What it does |
|---|---|---|---|
| 8 | Multipass and cloud-init | Systems/Linux Engineer | Creates a VM on your laptop and sets the first user |
| 9 | Ansible | Platform Engineer | Installs Docker, sets the firewall, and starts the app |
| 10 | Terraform | Cloud Engineer | Creates a VM and firewall on Google Cloud, then reuses the Ansible playbook |

## Tool commands

Ansible and Terraform run in containers. Run each command from the repository root.

```shell
docker compose -f tools/compose.yaml run --rm ansible ansible --version
docker compose -f tools/compose.yaml run --rm terraform version
docker compose -f tools/compose.yaml run --rm gcloud gcloud --version
```

On Windows PowerShell, set the `HOME` variable once per window. The compose file reads it:

```powershell
$env:HOME = $env:USERPROFILE
```

## Episode 7: Plan the infrastructure

Goal: you write a plan before you build anything.

1. Write one paragraph on the cloud basics in your plan:
   - The cloud is renting someone else's computers, on demand.
   - IaaS, PaaS, and SaaS differ by how much you manage. A Compute Engine VM is IaaS. A managed database is PaaS. Gmail is SaaS.
   - Choose a region and a zone close to your users.
2. List the parts of the app: Nginx, Flask, PostgreSQL. Each runs in a container.
3. Measure the memory of the running stack from Act 1:

   ```shell
   docker compose up -d --build
   docker stats --no-stream
   docker compose down -v
   ```

   The idle stack needs about 80 to 100 MB. Builds need more. Plan for 2 GB.
4. List the ports:

   | Port | Used by | Open to |
   |---|---|---|
   | 22 | SSH | Your IP address only (`/32`) |
   | 8080 | Web frontend | Everyone (`0.0.0.0/0`) |
   | 8000 and 5432 | Backend and database | Nobody (inside the Docker network) |

5. Plan the network. Use one VPC `10.0.0.0/16` and one subnet `10.0.1.0/24`. Write how many addresses each CIDR range holds: `/8` 16,777,216, `/16` 65,536, `/24` 256, `/32` 1.
6. Check that your VPC range is private. The three private ranges are `10.0.0.0/8`, `172.16.0.0/12`, and `192.168.0.0/16`. Look up a name with DNS:

   ```shell
   nslookup github.com
   ```

7. Draw a diagram: the internet, the firewall, the VPC, the subnet, the VM, the three containers. Write the CIDR range on the VPC and the subnet.
8. Open the [Google Cloud pricing calculator](https://cloud.google.com/products/calculator). Add one Compute Engine VM with 2 vCPUs and 2 GB of memory and a 20 GB disk. Write down the monthly cost.
9. Save your plan in `docs/infrastructure-plan.md`.

Concepts: IaaS, PaaS, SaaS, region, zone, sizing, capacity, least privilege, attack surface, port, CIDR, VPC, subnet, private address ranges (RFC1918), DNS, cost estimate, architecture diagram.

## Episode 8: Your first VM

Goal: you create a VM, log in with an SSH key, and run Linux commands.

1. Create an SSH key if you have none. Use an empty passphrase. The Ansible container has no ssh-agent. It cannot unlock a key that has a passphrase.

   ```shell
   ssh-keygen -t ed25519 -N ""
   ```

2. Write `infra/cloud-init/vm.yaml`:
   - Start the file with `#cloud-config`.
   - Set the host name to `taskboard`.
   - Create the user `student` with sudo rights and your public key.
   - Install `curl`, `git`, and `htop`.
3. Create the VM:

   ```shell
   multipass launch 24.04 --name taskboard --cpus 2 --memory 2G --disk 10G --cloud-init infra/cloud-init/vm.yaml
   multipass list
   ```

4. Log in with SSH. Use the IP address from `multipass list`:

   ```shell
   ssh student@<vm-ip>
   ```

5. Practice these Linux commands on the VM: `whoami`, `pwd`, `ls /`, `df -h`, `free -m`, `systemctl status ssh`, `sudo apt update`, `htop`.
6. Practice file commands: `cd`, `mkdir`, `touch`, `cat`, `cp`, `mv`, `rm`.
7. Change permissions. Run `ls -l`, then `chmod 400 notes.txt` and `chmod 755 notes.txt`.
8. Use a pipe and a redirect:

   ```shell
   cat /etc/passwd | grep student
   echo "hello cloud" > hello.txt
   echo "another line" >> hello.txt
   ```

9. Set and read an environment variable:

   ```shell
   export NAME="Task Board"
   echo "Hello, $NAME"
   ```

10. Write `report.sh`, make it executable, and save its output:

    ```bash
    #!/bin/bash
    echo "Report for ${1:-world} on $(hostname)"
    echo "Date: $(date)"
    df -h / | tail -n 1
    free -m | grep Mem
    ```

    ```shell
    chmod +x report.sh
    ./report.sh student > report.txt
    ```

11. Leave the VM. Keep it running for Episode 9.

Concepts: virtual machine, hypervisor, cloud-init, SSH key pair, sudo, package manager, systemd, file permissions, pipe, redirection, environment variable, shell script.

## Episode 9: Configuration as code

Goal: one command turns a blank VM into a running task board.

1. Copy the inventory example. Set the VM IP address:

   ```shell
   cp infra/ansible/inventory.example.ini infra/ansible/inventory.ini
   ```

2. Test the connection:

   ```shell
   docker compose -f tools/compose.yaml run --rm ansible ansible taskboard -m ping
   ```

3. Write `infra/ansible/playbook.yml` with these tasks, in order:
   - Install `docker.io`, `docker-compose-v2`, `ufw`, and `rsync` with the `apt` module.
   - Start Docker and enable it at boot.
   - Add the login user to the `docker` group.
   - Allow ports 22 and 8080 in UFW. Turn UFW on with the default policy `deny`.
   - Create `/opt/taskboard`.
   - Copy the app to the VM with `synchronize`. Skip `.git`, `infra`, and `.env`. Set `become: false` on this task only. `synchronize` under `become: true` writes files as root, which then fights the directory ownership the previous task set, and the playbook never reaches `changed=0`.
   - Write `.env` on the VM from the `DB_PASSWORD` variable. Set `no_log: true` and mode `0600`.
   - Start the stack with `community.docker.docker_compose_v2`.
4. Check the syntax:

   ```shell
   docker compose -f tools/compose.yaml run --rm ansible ansible-playbook --syntax-check playbook.yml
   ```

5. Run the playbook:

   ```shell
   export DB_PASSWORD=choose-a-password
   docker compose -f tools/compose.yaml run --rm -e DB_PASSWORD ansible ansible-playbook playbook.yml
   ```

   In PowerShell, set the variable with `$env:DB_PASSWORD = "choose-a-password"`.
6. Open `http://<vm-ip>:8080`. Add a task.
7. Run the playbook again. The recap must show `changed=0`. This is idempotence.
8. Check that port 8000 is closed. The command must time out:

   ```shell
   curl -m 3 http://<vm-ip>:8000/api/tasks
   ```

   This only times out because `compose.yaml` never publishes a backend port. Docker writes its own `iptables` rules for a published port, ahead of UFW's rules, so UFW's default-deny policy does not block a container port that is actually published to `0.0.0.0`. If you add one later for debugging, bind it to `127.0.0.1` only.

Concepts: configuration management, inventory, playbook, module, idempotence, firewall, secret handling.

## Episode 10: Now in the cloud

Goal: you create the same VM on Google Cloud with Terraform, and you destroy it.

Warning: this episode needs a Google Cloud free trial. Read [Costs and free options](costs-and-free-options.md) first. Create the budget alert in step 2 before you create any resource.

1. Create a Google Cloud project. Note the project ID.
2. In the Billing page, create a budget with an alert at a low amount, for example 5 USD.
3. Sign in. The command opens a browser:

   ```shell
   docker compose -f tools/compose.yaml run --rm gcloud gcloud auth application-default login
   docker compose -f tools/compose.yaml run --rm gcloud gcloud services enable compute.googleapis.com --project <project-id>
   ```

4. Look at `infra/terraform/gcp/versions.tf`. It sets the Google provider.
5. Write the resources:
   - `variables.tf`: project ID, region, zone, machine type, SSH public key, your IP in CIDR form.
   - `main.tf`: a network, a firewall rule for SSH from your IP only, a firewall rule for port 8080, and a Compute Engine VM with Ubuntu 24.04. The reference uses an auto-mode network. It does not create the `10.0.1.0/24` subnet from Episode 7. Add a `google_compute_subnetwork` resource if you want the exact plan.
   - `outputs.tf`: the VM IP address and the app URL.
6. Create `infra/terraform/gcp/terraform.tfvars` from your values. Never commit it.
7. Check the plan:

   ```shell
   docker compose -f tools/compose.yaml run --rm terraform init
   docker compose -f tools/compose.yaml run --rm terraform validate
   docker compose -f tools/compose.yaml run --rm terraform plan
   ```

8. Create the resources:

   ```shell
   docker compose -f tools/compose.yaml run --rm terraform apply
   ```

9. Put the VM IP address in `inventory.ini`. Set `ansible_user=student`. Run the Episode 9 playbook.
10. Open the app URL.
11. Destroy everything:

    ```shell
    docker compose -f tools/compose.yaml run --rm terraform destroy
    ```

12. Open the Billing page. Check that no resources remain.

Limits of one VM: it has one point of failure, it scales by hand, and each update is a playbook run. Act 3 solves these problems with Kubernetes.

Words to recognize (you do not build them): a load balancer spreads traffic across many servers. A reverse proxy forwards requests to another server, as the frontend Nginx does for `/api`. A CDN keeps copies of your files in cities around the world.

Concepts: infrastructure as code, provider, state file, plan and apply, firewall rule, budget alert, cost control, load balancer, reverse proxy, CDN.

## Clean up the local VM

Stop the Multipass VM before Act 3, because Minikube needs the memory:

```shell
multipass delete taskboard --purge
```

## Solution

The finished Act 2 is in the `solved` branch of this repository, folder `act-2-cloud-engineer/`.

## Act review

| | |
|---|---|
| Task | The app ran only on laptops. |
| What you did | Planned size, ports, and cost. Built a VM with cloud-init and Ansible. Built the same on Google Cloud with Terraform. Destroyed it. |
| What you achieved | A server you can rebuild from code. A second playbook run changes nothing. Only the needed ports are open. No resources are left running. |
| What comes next | The DevOps Engineer fixes the limits of one VM (Act 3). |

**Resume after Act 2:** use the headline "Junior Software Engineer with Cloud and Infrastructure as Code skills". Add the Act 2 rows of the [skills ledger](../cv/skills-ledger.md) to your CV.
