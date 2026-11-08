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

Try each task first. Open **Show solution** for that task only when you are stuck. The last line in each solution links to the `solved` branch. Use that link as a last resort.

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

#### Task 1: Write the cloud basics

Write one paragraph on the cloud basics in your plan.

<details>
<summary>Show solution</summary>

A sample paragraph:

> The cloud is renting someone else's computers, on demand. A Compute Engine VM is IaaS. A managed database is PaaS. Gmail is SaaS. I chose `us-central1` and `us-central1-a` because they are close to my users.

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

#### Task 2: List the parts

List the parts of the app: Nginx, Flask, PostgreSQL. Each runs in a container.

<details>
<summary>Show solution</summary>

| Part | Container |
|---|---|
| Nginx | `frontend` |
| Flask | `backend` |
| PostgreSQL | `database` |

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

#### Task 3: Measure the memory

Measure the memory of the running stack from Act 1.

<details>
<summary>Show solution</summary>

```shell
docker compose up -d --build
docker stats --no-stream
docker compose down -v
```

The idle stack needs about 80 to 100 MB. Builds need more. Plan for 2 GB.

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

#### Task 4: List the ports

List the ports and the source that may reach each one.

<details>
<summary>Show solution</summary>

| Port | Used by | Open to |
|---|---|---|
| 22 | SSH | Your IP address only (`/32`) |
| 8080 | Web frontend | Everyone (`0.0.0.0/0`) |
| 8000 and 5432 | Backend and database | Nobody (inside the Docker network) |

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

#### Task 5: Plan the network

Use one VPC `10.0.0.0/16` and one subnet `10.0.1.0/24`. Write how many addresses each CIDR range holds: `/8`, `/16`, `/24`, `/32`.

<details>
<summary>Show solution</summary>

| CIDR | Addresses |
|---|---|
| `/8` | 16,777,216 |
| `/16` | 65,536 |
| `/24` | 256 |
| `/32` | 1 |

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

#### Task 6: Check the private range and DNS

Check that your VPC range is private. The three private ranges are `10.0.0.0/8`, `172.16.0.0/12`, and `192.168.0.0/16`. Look up a name with DNS.

<details>
<summary>Show solution</summary>

`10.0.0.0/16` is inside `10.0.0.0/8`, so it is private. Look up a name:

```shell
nslookup github.com
```

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

#### Task 7: Draw the diagram

Draw a diagram: the internet, the firewall, the VPC, the subnet, the VM, the three containers. Write the CIDR range on the VPC and the subnet.

<details>
<summary>Show solution</summary>

Draw these boxes and arrows:

```text
Internet
  |
Firewall: 22 from your IP, 8080 from 0.0.0.0/0
  |
VPC 10.0.0.0/16
  |
Subnet 10.0.1.0/24
  |
VM
  |-- frontend container
  |-- backend container
  |-- database container
```

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

#### Task 8: Estimate the cost

Open the [Google Cloud pricing calculator](https://cloud.google.com/products/calculator). Add one Compute Engine VM with 2 vCPUs and 2 GB of memory and a 20 GB disk. Write down the monthly cost.

<details>
<summary>Show solution</summary>

In the calculator, select Compute Engine. Set 2 vCPUs, 2 GB memory, and a 20 GB disk in `us-central1`. Read the monthly estimate and write it in your plan. Prices change, so use the calculator.

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

#### Task 9: Save the plan

Save your plan in `docs/infrastructure-plan.md`.

<details>
<summary>Show solution</summary>

Fill these sections in `docs/infrastructure-plan.md`:

```text
# Infrastructure plan

## Parts

## Size

## Network

## Ports

## Cost

## Region, zone, and service model
```

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

Concepts: IaaS, PaaS, SaaS, region, zone, sizing, capacity, least privilege, attack surface, port, CIDR, VPC, subnet, private address ranges (RFC1918), DNS, cost estimate, architecture diagram.

## Episode 8: Your first VM

Goal: you create a VM, log in with an SSH key, and run Linux commands.

#### Task 1: Create an SSH key

Create an SSH key if you have none. Use an empty passphrase. The Ansible container has no ssh-agent. It cannot unlock a key that has a passphrase.

<details>
<summary>Show solution</summary>

```shell
ssh-keygen -t ed25519 -N ""
cat ~/.ssh/id_ed25519.pub
```

On Windows PowerShell, use `type $env:USERPROFILE\.ssh\id_ed25519.pub`.

Last resort: [open the solved cloud-init file](https://github.com/aliAljaffer/four-hats/blob/solved/act-2-cloud-engineer/infra/cloud-init/vm.yaml)

</details>

#### Task 2: Write the cloud-init file

Write `infra/cloud-init/vm.yaml`:

- Create the folder first: `mkdir -p infra/cloud-init`.
- Start the file with `#cloud-config`.
- Set the host name to `taskboard`.
- Create the user `student` with sudo rights and your public key.
- Install `curl`, `git`, and `htop`.

<details>
<summary>Show solution</summary>

```shell
mkdir -p infra/cloud-init
```

```yaml
#cloud-config
hostname: taskboard
users:
  - name: student
    groups: [sudo]
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - REPLACE_WITH_YOUR_PUBLIC_KEY
package_update: true
packages:
  - curl
  - git
  - htop
timezone: UTC
```

Last resort: [open the solved cloud-init file](https://github.com/aliAljaffer/four-hats/blob/solved/act-2-cloud-engineer/infra/cloud-init/vm.yaml)

</details>

#### Task 3: Create the VM

Create the VM with Multipass.

<details>
<summary>Show solution</summary>

```shell
multipass launch 24.04 --name taskboard --cpus 2 --memory 2G --disk 10G --cloud-init infra/cloud-init/vm.yaml
multipass list
```

Last resort: [open the solved cloud-init file](https://github.com/aliAljaffer/four-hats/blob/solved/act-2-cloud-engineer/infra/cloud-init/vm.yaml)

</details>

#### Task 4: Log in with SSH

Log in with SSH. Use the IP address from `multipass list`. Replace `VM_IP` with that address.

<details>
<summary>Show solution</summary>

```shell
ssh student@VM_IP
```

Last resort: [open the solved cloud-init file](https://github.com/aliAljaffer/four-hats/blob/solved/act-2-cloud-engineer/infra/cloud-init/vm.yaml)

</details>

#### Task 5: Practice Linux commands

Practice these Linux commands on the VM: `whoami`, `pwd`, `ls /`, `df -h`, `free -m`, `systemctl status ssh`, `sudo apt update`, `htop`.

<details>
<summary>Show solution</summary>

```shell
whoami
pwd
ls /
df -h
free -m
systemctl status ssh
sudo apt update
htop
```

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

#### Task 6: Practice file commands

Practice file commands: `cd`, `mkdir`, `touch`, `cat`, `cp`, `mv`, `rm`.

<details>
<summary>Show solution</summary>

```shell
cd /var/log
cd ..
cd ~
mkdir app
touch notes.txt
cat notes.txt
cp notes.txt copy.txt
mv copy.txt moved.txt
rm moved.txt
rm -r app
```

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

#### Task 7: Change permissions

Run `ls -l`, then change a file to `400` and then `755`.

<details>
<summary>Show solution</summary>

```shell
ls -l notes.txt
chmod 400 notes.txt
chmod 755 notes.txt
```

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

#### Task 8: Use a pipe and a redirect

Use a pipe and a redirect.

<details>
<summary>Show solution</summary>

```shell
cat /etc/passwd | grep student
echo "hello cloud" > hello.txt
echo "another line" >> hello.txt
cat hello.txt
```

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

#### Task 9: Set an environment variable

Set and read an environment variable.

<details>
<summary>Show solution</summary>

```shell
export NAME="Task Board"
echo "Hello, $NAME"
```

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

#### Task 10: Write a shell script

Write `report.sh`, make it executable, and save its output.

<details>
<summary>Show solution</summary>

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
cat report.txt
```

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

#### Task 11: Keep the VM running

Leave the VM. Keep it running for Episode 9.

<details>
<summary>Show solution</summary>

Type `exit` to leave the SSH session. Do not delete the VM.

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

Concepts: virtual machine, hypervisor, cloud-init, SSH key pair, sudo, package manager, systemd, file permissions, pipe, redirection, environment variable, shell script.

## Episode 9: Configuration as code

Goal: one command turns a blank VM into a running task board.

#### Task 1: Copy the inventory

Copy the inventory example. Set the VM IP address.

<details>
<summary>Show solution</summary>

```shell
cp infra/ansible/inventory.example.ini infra/ansible/inventory.ini
```

Edit `infra/ansible/inventory.ini`. Set `ansible_host` to the VM IP address.

Last resort: [open the solved inventory example](https://github.com/aliAljaffer/four-hats/blob/solved/act-2-cloud-engineer/infra/ansible/inventory.example.ini)

</details>

#### Task 2: Test the connection

Test the connection.

<details>
<summary>Show solution</summary>

```shell
docker compose -f tools/compose.yaml run --rm ansible ansible taskboard -m ping
```

Last resort: [open the solved playbook](https://github.com/aliAljaffer/four-hats/blob/solved/act-2-cloud-engineer/infra/ansible/playbook.yml)

</details>

#### Task 3: Write the playbook

Write `infra/ansible/playbook.yml` with these tasks, in order:

- Install `docker.io`, `docker-compose-v2`, `ufw`, and `rsync` with the `apt` module.
- Start Docker and enable it at boot.
- Add the login user to the `docker` group.
- Allow ports 22 and 8080 in UFW. Turn UFW on with the default policy `deny`.
- Create `/opt/taskboard`.
- Copy the app to the VM with `synchronize`. Skip `.git`, `infra`, and `.env`. Set `become: false` on this task only. `synchronize` under `become: true` writes files as root, which then fights the directory ownership the previous task set, and the playbook never reaches `changed=0`.
- Write `.env` on the VM from the `DB_PASSWORD` variable. Set `no_log: true` and mode `0600`.
- Start the stack with `community.docker.docker_compose_v2`.

<details>
<summary>Show solution</summary>

```yaml
- name: Deploy the task board
  hosts: taskboard
  become: true
  vars:
    app_dir: /opt/taskboard
    db_password: "{{ lookup('ansible.builtin.env', 'DB_PASSWORD') }}"
  tasks:
    - name: Install Docker and Compose
      ansible.builtin.apt:
        name:
          - docker.io
          - docker-compose-v2
          - ufw
          - rsync
        state: present
        update_cache: true

    - name: Start Docker at boot
      ansible.builtin.service:
        name: docker
        state: started
        enabled: true

    - name: Add the login user to the docker group
      ansible.builtin.user:
        name: "{{ ansible_user }}"
        groups: docker
        append: true

    - name: Allow SSH
      community.general.ufw:
        rule: allow
        port: "22"
        proto: tcp

    - name: Allow the web port
      community.general.ufw:
        rule: allow
        port: "8080"
        proto: tcp

    - name: Turn the firewall on
      community.general.ufw:
        state: enabled
        policy: deny

    - name: Create the app directory
      ansible.builtin.file:
        path: "{{ app_dir }}"
        state: directory
        owner: "{{ ansible_user }}"
        mode: "0755"

    - name: Copy the app
      become: false
      ansible.posix.synchronize:
        src: /repo/
        dest: "{{ app_dir }}/"
        recursive: true
        delete: false
        rsync_opts:
          - "--exclude=.git"
          - "--exclude=infra"
          - "--exclude=.env"
          - "--exclude=__pycache__"

    - name: Write the environment file
      ansible.builtin.copy:
        dest: "{{ app_dir }}/.env"
        content: "DB_PASSWORD={{ db_password }}\n"
        mode: "0600"
      no_log: true

    - name: Start the stack
      community.docker.docker_compose_v2:
        project_src: "{{ app_dir }}"
        build: policy
        state: present
```

Last resort: [open the solved playbook](https://github.com/aliAljaffer/four-hats/blob/solved/act-2-cloud-engineer/infra/ansible/playbook.yml)

</details>

#### Task 4: Check the syntax

Check the syntax.

<details>
<summary>Show solution</summary>

```shell
docker compose -f tools/compose.yaml run --rm ansible ansible-playbook --syntax-check playbook.yml
```

Last resort: [open the solved playbook](https://github.com/aliAljaffer/four-hats/blob/solved/act-2-cloud-engineer/infra/ansible/playbook.yml)

</details>

#### Task 5: Run the playbook

Run the playbook.

<details>
<summary>Show solution</summary>

```shell
export DB_PASSWORD=choose-a-password
docker compose -f tools/compose.yaml run --rm -e DB_PASSWORD ansible ansible-playbook playbook.yml
```

In PowerShell, set the variable with `$env:DB_PASSWORD = "choose-a-password"`.

Last resort: [open the solved playbook](https://github.com/aliAljaffer/four-hats/blob/solved/act-2-cloud-engineer/infra/ansible/playbook.yml)

</details>

#### Task 6: Open the app

Open `http://VM_IP:8080`. Add a task.

<details>
<summary>Show solution</summary>

Open `http://VM_IP:8080` in a browser. Add a task. The task appears in the list.

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

#### Task 7: Check idempotence

Run the playbook again. The recap must show `changed=0`. This is idempotence.

<details>
<summary>Show solution</summary>

```shell
export DB_PASSWORD=choose-a-password
docker compose -f tools/compose.yaml run --rm -e DB_PASSWORD ansible ansible-playbook playbook.yml
```

The recap must show `changed=0`.

Last resort: [open the solved playbook](https://github.com/aliAljaffer/four-hats/blob/solved/act-2-cloud-engineer/infra/ansible/playbook.yml)

</details>

#### Task 8: Check that port 8000 is closed

Check that port 8000 is closed. The command must time out.

<details>
<summary>Show solution</summary>

```shell
curl -m 3 http://VM_IP:8000/api/tasks
```

This only times out because `compose.yaml` never publishes a backend port. Docker writes its own `iptables` rules for a published port, ahead of UFW's rules, so UFW's default-deny policy does not block a container port that is actually published to `0.0.0.0`. If you add one later for debugging, bind it to `127.0.0.1` only.

Last resort: [open the solved playbook](https://github.com/aliAljaffer/four-hats/blob/solved/act-2-cloud-engineer/infra/ansible/playbook.yml)

</details>

Concepts: configuration management, inventory, playbook, module, idempotence, firewall, secret handling.

## Episode 10: Now in the cloud

Goal: you create the same VM on Google Cloud with Terraform, and you destroy it.

Warning: this episode needs a Google Cloud free trial. Read [Costs and free options](costs-and-free-options.md) first. Create the budget alert in task 2 before you create any resource.

#### Task 1: Create a Google Cloud project

Create a Google Cloud project. Note the project ID.

<details>
<summary>Show solution</summary>

Open the Google Cloud console. Create a project. Copy the project ID. You need it in `terraform.tfvars`.

Last resort: [open the solved Terraform folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer/infra/terraform/gcp)

</details>

#### Task 2: Create a budget alert

In the Billing page, create a budget with an alert at a low amount, for example 5 USD.

<details>
<summary>Show solution</summary>

Open **Billing > Budgets and alerts**. Select **Create budget**. Set the amount to 5 USD. Add an email alert at 50 percent, 90 percent, and 100 percent.

Last resort: [open the solved Terraform folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer/infra/terraform/gcp)

</details>

#### Task 3: Sign in and enable the API

Sign in. The command opens a browser. Enable the Compute Engine API. Replace `PROJECT_ID` with your project ID.

<details>
<summary>Show solution</summary>

```shell
docker compose -f tools/compose.yaml run --rm gcloud gcloud auth application-default login
docker compose -f tools/compose.yaml run --rm gcloud gcloud services enable compute.googleapis.com --project PROJECT_ID
```

Last resort: [open the solved Terraform folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer/infra/terraform/gcp)

</details>

#### Task 4: Read the provider file

Look at `infra/terraform/gcp/versions.tf`. It sets the Google provider.

<details>
<summary>Show solution</summary>

The file sets the Google provider version and the `project`, `region`, and `zone` inputs. You do not change it.

Last resort: [open the solved versions.tf](https://github.com/aliAljaffer/four-hats/blob/solved/act-2-cloud-engineer/infra/terraform/gcp/versions.tf)

</details>

#### Task 5: Write the Terraform resources

Write the resources:

- `variables.tf`: project ID, region, zone, machine type, SSH public key, your IP in CIDR form.
- `main.tf`: a network, a firewall rule for SSH from your IP only, a firewall rule for port 8080, and a Compute Engine VM with Ubuntu 24.04. The reference uses an auto-mode network. It does not create the `10.0.1.0/24` subnet from Episode 7. Add a `google_compute_subnetwork` resource if you want the exact plan.
- `outputs.tf`: the VM IP address and the app URL.

<details>
<summary>Show solution</summary>

`variables.tf`:

```hcl
variable "project_id" {
  description = "Your GCP project ID"
  type        = string
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "zone" {
  type    = string
  default = "us-central1-a"
}

variable "machine_type" {
  type    = string
  default = "e2-small"
}

variable "ssh_public_key" {
  description = "Contents of your public key file"
  type        = string
}

variable "ssh_user" {
  type    = string
  default = "student"
}

variable "allowed_ssh_cidr" {
  description = "Your public IP in CIDR form, for example 203.0.113.7/32"
  type        = string
}
```

`main.tf`:

```hcl
resource "google_compute_network" "taskboard" {
  name                    = "taskboard"
  auto_create_subnetworks = true
}

resource "google_compute_firewall" "ssh" {
  name          = "taskboard-allow-ssh"
  network       = google_compute_network.taskboard.name
  source_ranges = [var.allowed_ssh_cidr]
  target_tags   = ["taskboard"]

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
}

resource "google_compute_firewall" "web" {
  name          = "taskboard-allow-web"
  network       = google_compute_network.taskboard.name
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["taskboard"]

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }
}

resource "google_compute_instance" "taskboard" {
  name         = "taskboard"
  machine_type = var.machine_type
  tags         = ["taskboard"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2404-lts-amd64"
      size  = 20
    }
  }

  network_interface {
    network = google_compute_network.taskboard.name
    access_config {}
  }

  metadata = {
    ssh-keys = "${var.ssh_user}:${var.ssh_public_key}"
  }
}
```

`outputs.tf`:

```hcl
output "vm_ip" {
  value = google_compute_instance.taskboard.network_interface[0].access_config[0].nat_ip
}

output "app_url" {
  value = "http://${google_compute_instance.taskboard.network_interface[0].access_config[0].nat_ip}:8080"
}
```

Last resort: [open the solved Terraform folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer/infra/terraform/gcp)

</details>

#### Task 6: Create the values file

Create `infra/terraform/gcp/terraform.tfvars` from your values. Never commit it.

<details>
<summary>Show solution</summary>

```hcl
project_id       = "your-project-id"
ssh_public_key   = "ssh-ed25519 AAAA... you@laptop"
allowed_ssh_cidr = "203.0.113.7/32"
```

Last resort: [open the solved tfvars example](https://github.com/aliAljaffer/four-hats/blob/solved/act-2-cloud-engineer/infra/terraform/gcp/terraform.tfvars.example)

</details>

#### Task 7: Check the plan

Check the plan.

<details>
<summary>Show solution</summary>

```shell
docker compose -f tools/compose.yaml run --rm terraform init
docker compose -f tools/compose.yaml run --rm terraform validate
docker compose -f tools/compose.yaml run --rm terraform plan
```

Last resort: [open the solved Terraform folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer/infra/terraform/gcp)

</details>

#### Task 8: Create the resources

Create the resources.

<details>
<summary>Show solution</summary>

```shell
docker compose -f tools/compose.yaml run --rm terraform apply
```

Last resort: [open the solved Terraform folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer/infra/terraform/gcp)

</details>

#### Task 9: Run the playbook on the cloud VM

Put the VM IP address in `inventory.ini`. Set `ansible_user=student`. Run the Episode 9 playbook.

<details>
<summary>Show solution</summary>

Edit `infra/ansible/inventory.ini`. Set `ansible_host` to the VM IP address and `ansible_user=student`. Run:

```shell
export DB_PASSWORD=choose-a-password
docker compose -f tools/compose.yaml run --rm -e DB_PASSWORD ansible ansible-playbook playbook.yml
```

Last resort: [open the solved playbook](https://github.com/aliAljaffer/four-hats/blob/solved/act-2-cloud-engineer/infra/ansible/playbook.yml)

</details>

#### Task 10: Open the app

Open the app URL.

<details>
<summary>Show solution</summary>

Open `http://VM_IP:8080` in a browser. Add a task.

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

#### Task 11: Destroy the resources

Destroy everything.

<details>
<summary>Show solution</summary>

```shell
docker compose -f tools/compose.yaml run --rm terraform destroy
```

Last resort: [open the solved Terraform folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer/infra/terraform/gcp)

</details>

#### Task 12: Check the Billing page

Open the Billing page. Check that no resources remain.

<details>
<summary>Show solution</summary>

Open **Billing > Reports**. Check that no Compute Engine VM, disk, or network remains. Open **Compute Engine > VM instances** and **Compute Engine > Disks**. Both lists must be empty.

Last resort: [open the solved Act 2 folder](https://github.com/aliAljaffer/four-hats/tree/solved/act-2-cloud-engineer)

</details>

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
