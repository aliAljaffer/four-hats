# ALL-01: Set up your laptop

**Introduction** · Focus: overview · About 18 minutes

You install five programs and pull three container images. After this episode, every later episode runs on your laptop without a setup detour.

| | |
|---|---|
| You need | macOS or Windows 10/11, administrator access, 8 GB of memory or more, 30 GB of free disk |
| You build | A working toolchain and a fork of the starter repository |
| Done when | Four version commands print, three images exist, and the course test tool prints `Ran 3 tests` and `OK` |

## What you will be able to do

- Explain what each of the five tools does.
- Install the tools on macOS with Homebrew or on Windows with Winget.
- Check every install with a version command.
- Give Docker Desktop enough CPU and memory for Kubernetes.
- Pull the three course images before you need them.
- Fork and clone the starter repository.
- Run the course test tool to prove the setup works.

## Before you start

- macOS or Windows 10/11.
- An account with administrator rights, so you can install software.
- 8 GB of memory or more. 16 GB is better.
- 30 GB of free disk space.

## The five tools

| Tool | Why you need it | Act |
|---|---|---|
| Git | Version control. You push and pull code from GitHub. | All |
| VS Code | Code editor for Python, JavaScript, YAML, and shell. | All |
| Docker Desktop | Runs containers for the app, the database, and the course tools. | All |
| Multipass | Runs Ubuntu virtual machines on your laptop. | 2 |
| Minikube | Runs a Kubernetes cluster with one node. | 3 and 4 |

Three of the five are ways to run something: Docker runs containers, Multipass runs VMs, Minikube runs Kubernetes. Git stores history, and VS Code edits files.

The course keeps the tool count small on purpose. Everything else runs as a container image that you pull once.

## macOS: Homebrew

Homebrew is the package manager for macOS. Check whether it exists before you install anything.

If Homebrew is missing, run its install script from [brew.sh](https://brew.sh). The script asks for your password and takes about a minute.

Then install the five programs:

```shell
brew install git minikube
brew install --cask visual-studio-code docker-desktop multipass
```

`brew install` is for command-line formulas. `--cask` is for graphical applications. Git and Minikube are formulas; VS Code, Docker Desktop, and Multipass are casks.

Open Docker Desktop once after the install. Accept the terms and wait until it shows "Engine running". The first start can take a couple of minutes while it creates its VM.

## Windows: Winget and WSL2

Open PowerShell as Administrator. Docker Desktop and Multipass both need the Virtual Machine Platform, which WSL2 provides.

```powershell
wsl --install --no-distribution
```

Restart the computer when the command finishes. Then open PowerShell as Administrator again and install the programs:

```powershell
winget install -e --id Git.Git
winget install -e --id Microsoft.VisualStudioCode
winget install -e --id Docker.DockerDesktop
winget install -e --id Canonical.Multipass
winget install -e --id Kubernetes.minikube
```

Open Docker Desktop and make sure it uses Linux containers, not Windows containers. The setting is in the system tray menu.

Use PowerShell for every course command. Do not run the commands inside WSL, even though you enabled it. The course paths and Docker contexts assume PowerShell.

## Check the install

Run each command. Each one should print a version.

```shell
git --version
docker version
multipass version
minikube version
```

If one fails, the install did not finish or the program is not on `PATH`. Fix it now. A missing tool stops the act that needs it.

`docker version` is the most common failure. Docker Desktop must be running, not just installed. The command talks to the Docker engine, not to the desktop app.

## Give Docker enough resources

Kubernetes needs CPU and memory. In Docker Desktop, open **Settings**, then **Resources**.

Set these values:

| Resource | Minimum | Why |
|---|---|---|
| CPUs | 6 | Kubernetes and the app run side by side. |
| Memory | 8 GB | The control plane and the workloads need room. |

Docker Desktop restarts when you apply the settings. If your laptop has less than 8 GB in total, Acts 1 and 2 still work. See [Costs and free options](../costs-and-free-options.md) for the alternatives.

## Pull the images early

Container images are large. Pull them now so the first episode that needs them does not wait.

```shell
docker pull python:3.12-slim
docker pull postgres:16-alpine
docker pull nginx:1.27-alpine
```

Three images cover Acts 1 and 2. Acts 3 and 4 add more, and those episodes pull what they need.

The tags matter. `3.12-slim`, `16-alpine`, and `1.27-alpine` are pinned versions. A later episode builds on the same base, so the pull is reused.

## Fork and clone

Open the starter repository on GitHub and select **Fork**. The fork is your copy, under your account. You can push to it, and the course can see it without giving you write access to the original.

Clone your fork:

```shell
git clone https://github.com/YOUR-USERNAME/minikube-project.git
cd minikube-project
```

Replace `YOUR-USERNAME` with your GitHub username. The folder name is `minikube-project`.

Open the folder in VS Code. The repository recommends seven extensions: Docker, YAML, Kubernetes, Terraform, Ansible, GitHub Actions, and Semgrep. Select **Install All**. Later episodes use each one, and none of them needs a manual search.

## Prove the setup works

The starter includes a test tool that runs in a container. Run it from the repository root:

```shell
docker compose -f tools/compose.yaml run --rm python-test
```

Expected output:

```text
Ran 3 tests in 0.2s

OK
```

Three tests pass on the starter code. Episode 4 adds the first feature test.

If this command works, Docker can build an image, mount the code, install the requirements, and run Python. That is the whole toolchain in one check.

## Common mistakes

- **Not opening Docker Desktop.** The engine must run. `docker version` fails otherwise.
- **Running Minikube inside WSL.** Use PowerShell for every course command on Windows.
- **Using `curl` in PowerShell 5.1.** PowerShell maps `curl` to an alias. Use `curl.exe` when a command needs the real program.
- **Too little memory for Docker.** Below 8 GB, Kubernetes in Act 3 is slow or fails to start.
- **Disk full during pulls.** Images are large. Run `docker image prune` if space runs short.
- **Cloning the original repository instead of the fork.** You cannot push to the original. Clone your fork.
- **Skipping the test tool check.** A setup that has not run a container is an assumption, not a working setup.

## Check your work

- [ ] `git --version` prints a version.
- [ ] `docker version` prints a client and a server version.
- [ ] `multipass version` prints a version.
- [ ] `minikube version` prints a version.
- [ ] Docker Desktop has at least 6 CPUs and 8 GB of memory.
- [ ] The three base images exist in `docker images`.
- [ ] Your fork exists on GitHub and is cloned on the laptop.
- [ ] The test tool prints `Ran 3 tests` and `OK`.

## What this unlocks on your CV

No ledger rows yet. You are setting up, not building a skill. Episode 2 adds the first row: Git and GitHub.

## Career note

A software engineer uses these tools every day. Git manages the change, VS Code writes it, Docker runs it locally, and GitHub backs it up and opens it for review. The setup is not the job, but a broken setup stops the job.

## Next

Episode 2 makes your first change: a branch, a commit, a push, a pull request, and a merge.

## Apply

The verified steps for this episode are in [Setup](../00-setup.md). Follow the tasks for your operating system.

<!-- APPLY -->

### What you should see

| After | You should see |
|---|---|
| You run the version commands | One version line per tool. |
| You open Docker Desktop | "Engine running" in the status bar. |
| You pull the images | Three completed pulls in `docker images`. |
| You fork and clone | A `minikube-project` folder with the repository files. |
| You open the folder in VS Code | A prompt to install the recommended extensions. |
| You run the test tool | `Ran 3 tests` and `OK`. |

An end-to-end run of this setup passed: the three images pulled and the test tool printed `Ran 3 tests ... OK`.
