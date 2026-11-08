# Setup (Episode 1)

You install five programs on your laptop. All other tools run as Docker images, so you do not install them.

| Program | Why you need it |
|---|---|
| Git | Version control |
| VS Code | Code editor |
| Docker Desktop | Runs containers and the course tools |
| Multipass | Runs Ubuntu VMs (Act 2) |
| Minikube | Runs a local Kubernetes cluster (Act 3 and 4) |

## macOS

1. Install Homebrew from [brew.sh](https://brew.sh) if you do not have it.
2. Install the programs:

   ```shell
   brew install git minikube
   brew install --cask visual-studio-code docker-desktop multipass
   ```

3. Open Docker Desktop once. Accept the terms. Wait until it shows "Engine running".

## Windows 10/11

1. Open PowerShell as Administrator.
2. Turn on the Virtual Machine Platform feature. Docker Desktop (WSL2) and Multipass both need it.

   ```powershell
   wsl --install --no-distribution
   ```

3. Restart your computer.
4. Install the programs:

   ```powershell
   winget install -e --id Git.Git
   winget install -e --id Microsoft.VisualStudioCode
   winget install -e --id Docker.DockerDesktop
   winget install -e --id Canonical.Multipass
   winget install -e --id Kubernetes.minikube
   ```

5. Open Docker Desktop once. Make sure it uses Linux containers.
6. Use PowerShell for all course commands. Do not run Minikube inside WSL.

## Check the install

Run each command. Each one must print a version.

```shell
git --version
docker version
multipass version
minikube version
```

## Configure Docker Desktop resources

Kubernetes needs room. In Docker Desktop, open **Settings > Resources**.

1. Set CPUs to 6 or more.
2. Set memory to 8 GB or more.

If your laptop has less, you can still do Acts 1 and 2. See [Costs and free options](costs-and-free-options.md) for other choices.

## Pull the course images

Pull the images now, so episodes do not wait for downloads:

```shell
docker pull python:3.12-slim
docker pull postgres:16-alpine
docker pull nginx:1.27-alpine
```

Later acts add more images. Each act doc lists them.

## Port conflicts

Some steps use host ports 8000 and 8080. If another program uses them, use 18000 and 18080. Change the host port in the command and in the URL. The container port does not change.

## Run course tools

Course tools run from `tools/compose.yaml`. The command is the same on macOS and Windows:

```shell
docker compose -f tools/compose.yaml run --rm python-test
```

This runs the backend tests in a Python container.

## Fork the repository

1. Sign in to GitHub.
2. Open the starter repository at https://github.com/aliAljaffer/four-hats and select **Fork**.
3. Clone your fork:

   ```shell
   git clone https://github.com/YOUR_USERNAME/four-hats.git
   cd four-hats
   ```

4. Open the folder in VS Code. It suggests a set of extensions for this repository. Select **Install All**.
