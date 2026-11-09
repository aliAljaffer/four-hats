# CLD-09: Configuration as code

**Act 2, Cloud Engineer** · Focus: platform engineer · About 20 to 25 minutes

One command now builds the server. Ansible installs Docker, sets the firewall, writes the secrets, and starts the task board on the VM from Episode 8. You write the steps once. You run them on every server, every time.

| | |
|---|---|
| You need | Episode 8 complete. A running VM with your SSH key. Docker Desktop running. |
| You build | An Ansible inventory and playbook that turns a blank VM into a running task board |
| Done when | The playbook ends with `failed=0`, a second run shows `changed=0`, and only ports 22 and 8080 are open |

## What you will be able to do

- Explain configuration management and idempotence.
- Write an Ansible inventory and playbook.
- Run Ansible from a container.
- Set a firewall with UFW.
- Pass a secret without writing it in Git.

## Before you start

- Episode 8 complete. A VM is running and your SSH key works.
- Docker Desktop is running, so the Ansible container can start.
- You can open a terminal in the repository.

## Manual setup does not scale

Imagine you have to set up ten servers by hand. You will forget a step on server seven. That one forgotten step is drift. The servers look the same, but they are not the same.

Ansible removes the memory problem. You write each step once as a task. Ansible runs the same tasks on every server. Every server converges to the same state.

Configuration management means describing the wanted state in code. Ansible compares the live server with the wanted state. It changes only what differs. Idempotence means a second run changes nothing. The second run reports `changed=0`. You can run the playbook any time, without fear of breaking the server.

## Ansible runs in a container

We do not install Ansible on the laptop. It runs as a Docker image. The image comes from `tools/ansible/Dockerfile`.

```shell
docker compose -f tools/compose.yaml run --rm ansible ansible --version
```

Ansible connects to the VM over SSH. It needs nothing installed on the VM. The VM only needs the `student` user and the packages the playbook installs.

```shell
cp infra/ansible/inventory.example.ini infra/ansible/inventory.ini
```

Edit the IP address in `inventory.ini`. Then test the connection:

```shell
docker compose -f tools/compose.yaml run --rm ansible ansible taskboard -m ping
```

On Windows PowerShell, run `$env:HOME = $env:USERPROFILE` first. Compose needs it to find your SSH key.

On a real server, use a passphrase and an agent. For this lab, create the key without a passphrase: `ssh-keygen -t ed25519 -N ""`. The Ansible container has no ssh-agent. It cannot unlock a key that has a passphrase.

## Inventory, playbook, and modules

| Term | Meaning |
|---|---|
| Inventory | The list of servers. One line per VM, with its IP address. |
| Playbook | An ordered list of tasks. Each task calls a module. |
| Module | A plugin that performs one kind of change. |
| Idempotence | Running twice changes nothing the second time. |
| Host firewall | UFW with default policy `deny`, plus allow rules by port. |
| Secret handling | Password from the environment, hidden with `no_log`. |

A playbook is a list of tasks. Each task calls a module. You describe the state you want. Ansible decides what to change.

The playbook for this episode does the following, in order:

1. Install packages with `ansible.builtin.apt`: `docker.io`, `docker-compose-v2`, `ufw`, and `rsync`.
2. Start Docker and enable it at boot with `ansible.builtin.service`.
3. Add the login user to the `docker` group with `ansible.builtin.user`.
4. Set the firewall with `community.general.ufw`: allow 22 and 8080, then turn UFW on with policy `deny`.
5. Create the app directory and copy the app with `ansible.posix.synchronize`. Skip `.git`, `infra`, and `.env`. Set `become: false` on this one task.
6. Write `.env` with `ansible.builtin.copy`. Set mode `0600` and `no_log: true`.
7. Start the stack with `community.docker.docker_compose_v2`.

The `synchronize` step needs `become: false`. `synchronize` under `become: true` writes files as root. That fights the ownership the directory task set. The playbook then never settles. Turn privilege escalation off for just this one task.

## Check and run

Check the syntax before you run:

```shell
docker compose -f tools/compose.yaml run --rm ansible ansible-playbook --syntax-check playbook.yml
export DB_PASSWORD=choose-a-password
docker compose -f tools/compose.yaml run --rm -e DB_PASSWORD ansible ansible-playbook playbook.yml
```

Each task shows `ok` or `changed`. The recap shows `failed=0`. The run takes a few minutes, because the VM builds the images.

Open `http://<vm-ip>:8080` in a browser and add a task. The task appears in the list.

Port 8000 must stay closed:

```shell
curl -m 3 http://<vm-ip>:8000/api/tasks
```

The command times out. The firewall works. Only the ports from our plan are open.

This only holds because `compose.yaml` never publishes a backend port. A published container port bypasses UFW entirely, because Docker writes its own rules ahead of it. The UFW default-deny policy cannot block a container port that is actually published. If you add a published port later for debugging, bind it to `127.0.0.1` only.

## Secrets stay out of Git

The password comes from the `DB_PASSWORD` environment variable. It is never in Git.

Pass it to the container with `-e DB_PASSWORD`. The playbook reads it with a lookup and writes it into `.env` on the VM with mode `0600`. `no_log: true` hides the password from the output.

Both `inventory.ini` and `.env` are in `.gitignore`. Never commit them. The inventory holds a live IP address. The `.env` holds a live password.

Repeatability beats memory. Secrets stay out of Git. Firewalls enforce the plan. Only planned ports are open.

## Run it twice to prove it

Run the playbook again:

```shell
docker compose -f tools/compose.yaml run --rm -e DB_PASSWORD ansible ansible-playbook playbook.yml
```

`changed=0`. Nothing changed, because the VM already has the wanted state. This is idempotence. You can run the playbook any time.

The playbook is documentation that runs. A teammate reads it in Git and sees how the server is set up. When a server breaks, you rebuild it from the playbook.

## Common mistakes

- **Turning UFW on before you allow port 22.** SSH stops working.
- **Wrong IP address in `inventory.ini`.** Run `multipass list`.
- **Committing `inventory.ini` or `.env`.** Both are in `.gitignore`.
- **Forgetting `-e DB_PASSWORD`.** The container cannot see the variable.
- **YAML indentation errors.** Run `--syntax-check`.
- **Windows: not setting `$env:HOME`.** Compose cannot find your SSH key.
- **A private key with a passphrase.** The Ansible container has no ssh-agent. Create the key without a passphrase, or load the key into an agent on the host.

## Check your work

- [ ] `ansible taskboard -m ping` returns `SUCCESS` and `"ping": "pong"`.
- [ ] `ansible-playbook --syntax-check` passes without errors.
- [ ] The playbook finishes with `failed=0`.
- [ ] The app loads at `http://<vm-ip>:8080` and an added task appears in the list.
- [ ] `curl -m 3 http://<vm-ip>:8000/api/tasks` times out.
- [ ] A second playbook run shows `changed=0`.
- [ ] `.env` on the VM has mode `0600` and the password does not appear in the output.
- [ ] `inventory.ini` and `.env` are not committed.

## What this unlocks on your CV

| Skill | Episode | CV section | Example bullet |
|---|---|---|---|
| Ansible | 9 | Cloud and Infrastructure | Wrote an idempotent Ansible playbook that installs Docker, sets the firewall, and deploys a Compose stack |
| Firewalls (UFW, VPC rules) | 9, 10 | Cloud and Infrastructure | Closed all ports except SSH and HTTP with UFW and GCP firewall rules |

## Career note

A platform engineer writes the setup once and lets the playbook run it. Each hand fix is a change nobody wrote down and nobody can repeat. The playbook replaces hand work with a repeatable run. A teammate can read it, review it, and rebuild a broken server from it.

## Next

Episode 10 runs the same playbook on a VM in Google Cloud. Terraform creates that VM. Only the IP address changes.

## Apply

The verified steps for this episode are in [Act 2, Episode 9](../act2-cloud-engineer.md#episode-9-configuration-as-code). Follow the tasks in order.

<!-- APPLY -->

### What you should see

| After | You should see |
|---|---|
| You test the connection | `SUCCESS` and `"ping": "pong"`. |
| You run the playbook | Each task `ok` or `changed`, and `failed=0`. The run takes a few minutes. |
| You open the app | The task board at `http://<vm-ip>:8080` loads, and an added task appears in the list. |
| You probe port 8000 | `curl -m 3 http://<vm-ip>:8000/api/tasks` times out. |
| You run the playbook again | `changed=0`. |

An end-to-end run of this episode passed: Ansible ping returned `pong`, the playbook finished with `failed=0`, the second stable run showed `changed=0`, and port 8000 timed out.
