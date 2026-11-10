# CLD-07: Plan the infrastructure

**Act 2, Cloud Engineer** · Focus: cloud architect · About 27 minutes

Your app runs on your laptop. Users cannot reach your laptop. This episode decides where it runs, how big the server is, which ports open, and what it costs. You build nothing yet.

| | |
|---|---|
| You need | Episode 5 complete. `docker compose up` works. A browser for the pricing calculator. |
| You build | A one-page infrastructure plan: parts, size, network, ports, cost |
| Done when | The plan names the service model, region, zone, VM size, [[gcp/vpc|VPC]] and subnet, open ports, and monthly cost |

## What you will be able to do

- Explain what the cloud is and tell IaaS, PaaS, and SaaS apart.
- Name a region, a zone, an instance, and an image.
- Size a VM from measured data, not a guess.
- Decide which ports to open and to whom.
- Read [[cloud/cidr|CIDR]] notation and plan one VPC with one subnet.
- Name the three private address ranges.
- Resolve a name with `nslookup`.
- Draw an architecture diagram for review.
- Estimate a monthly cost with the GCP pricing calculator.

## Before you start

- Episode 5 complete. The Compose stack starts with one command.
- Docker Desktop is running, so you can measure the stack.
- You can open a browser and a text editor.

## What the cloud is

The cloud is renting someone else's computers over the internet, on demand. You pay for what you use. The provider owns the data centres and rents slices through a console and an API.

| Buy your own server | Rent from the cloud |
|---|---|
| Large cost up front | Cents per hour |
| Days to arrive and install | About a minute to start |
| You replace failed hardware | The provider replaces it |
| You own the capacity | You rent the capacity |

Four words cover the geography and the unit:

| Word | Meaning |
|---|---|
| Region | A geographic area with data centres. Pick one near your users. |
| Zone | An isolated data centre inside a region. |
| Instance | One running VM. |
| Image | The template an instance starts from. |

One question sorts every cloud service: how much do you manage, and how much does the provider manage?

| Model | You manage | Provider manages | Example |
|---|---|---|---|
| IaaS | Operating system, runtime, app | Hardware, network | A [[gcp/compute-engine|Compute Engine]] VM. This act. |
| PaaS | Your app and data | Everything else | A managed database |
| SaaS | Nothing, you log in | All of it | Gmail, GitHub |

This act starts at IaaS. You get the most control and the most work.

## Measure before you size

Do not guess the size of a server. Start the stack and measure it:

```shell
docker compose up -d --build
docker stats --no-stream
```

The idle stack is small: about 8 MB for the frontend, 50 MB for the backend, and 30 MB for the database. The build phase needs more memory than the running app.

Plan for 2 vCPUs and 2 GB of memory. That covers the app, a build, and room for the operating system. Disk adds the image, the database volume, and logs. Twenty GB is a reasonable starting point for this lab.

Sizing from a guess produces one of two failures. Too small, and the build or the database dies under load. Too large, and you pay for capacity nobody uses.

## Ports and [[cloud/principle-of-least-privilege|least privilege]]

Every open port is a way in. Open as few as you can.

| Port | Used by | Open to |
|---|---|---|
| 22 | SSH | Your IP address only, as `/32` |
| 8080 | Web frontend | Everyone, `0.0.0.0/0` |
| 8000 and 5432 | Backend and database | Nobody |

A port is a numbered door on the server. One machine runs many services, one per port. Well-known ports are 22 for SSH, 80 for HTTP, and 443 for HTTPS. This app uses 8080 for the web page.

A firewall rule has three parts: port, protocol, and source. A rule with source `10.0.0.0/16` blocks a request from the internet, even if the port is open. The source decides who can connect.

The backend and the database talk inside the Docker network on the VM. They need no public port. That is least privilege applied to the network.

## CIDR and subnets

A firewall rule needs an address range. CIDR writes that range.

An IPv4 address has 32 bits. The number after the slash says how many bits are fixed. The remaining bits are free for hosts. The number of addresses is 2 to the power of (32 minus the prefix).

| CIDR | Example | Addresses | Use |
|---|---|---|---|
| `/8` | `10.0.0.0/8` | 16,777,216 | A very large private network |
| `/16` | `10.0.0.0/16` | 65,536 | One VPC |
| `/24` | `10.0.1.0/24` | 256 | One subnet |
| `/32` | `203.0.113.7/32` | 1 | One machine, such as your own IP |

A VPC is your private network in the cloud. A subnet is a slice of it. The cloud reserves a few addresses in every subnet, so you get fewer usable addresses than the count suggests.

The plan uses one VPC at `10.0.0.0/16`, one subnet at `10.0.1.0/24`, and one VM inside it. SSH opens from your IP as `/32`. The web port opens from `0.0.0.0/0`.

`0.0.0.0/0` means every address. Reserve it for the public web port. Never use it for SSH or a database.

## Private addresses and DNS

Three ranges are reserved for private networks. They never appear on the public internet. This is RFC1918.

| Range | Addresses |
|---|---|
| `10.0.0.0/8` | `10.x.x.x` |
| `172.16.0.0/12` | `172.16.x.x` to `172.31.x.x` |
| `192.168.0.0/16` | `192.168.x.x` |

The VM has a private address inside the VPC. It also needs a public address so users can reach it. DNS maps a name to that public address. Look one up:

```shell
nslookup github.com
```

The command returns one or more addresses. A domain name points at the public address of the VM, or at a load balancer in front of it.

## Draw the plan

A diagram lets the team check the plan before anyone spends money. Draw six things:

1. The internet.
2. The firewall, with port 22 and port 8080 marked.
3. The VPC, with its CIDR.
4. The subnet, with its CIDR.
5. The VM.
6. The three containers.

Save the diagram next to the plan. A wrong size or an open port costs nothing to fix now. After the build, it costs an incident.

## Estimate the cost

Cloud bills surprise people. Estimate first.

In the Google Cloud pricing calculator:

1. Add a Compute Engine instance.
2. Set 2 vCPUs, 2 GB of memory, and a 20 GB disk.
3. Read the monthly estimate.

Write the number in the plan. Prices change, so use the calculator, not a video. A VM costs money for every hour it runs, even when nobody uses it.

## Common mistakes

- **Sizing from a guess.** Measure with `docker stats`.
- **Opening port 5432 to the internet.** Databases stay private.
- **Opening SSH to everyone.** Allow your IP only, as `/32`.
- **Forgetting the disk in the cost estimate.** The disk has a monthly price.
- **Mixing up `/24` and `/32`.** A `/24` has 256 addresses. A `/32` has one.
- **Using `0.0.0.0/0` for SSH.** That opens SSH to the world.
- **Picking a public range for the VPC.** Use RFC1918.
- **Thinking an open port means everyone can reach it.** The source range decides.

## Check your work

- [ ] The plan names the service model, IaaS.
- [ ] The plan names a region and a zone.
- [ ] The VM size comes from a measurement, not a guess.
- [ ] The VPC and subnet use RFC1918 ranges.
- [ ] SSH opens from your IP as `/32`.
- [ ] The web port opens from `0.0.0.0/0`.
- [ ] The database and backend have no public port.
- [ ] The diagram shows internet, firewall, VPC, subnet, VM, and containers.
- [ ] The monthly cost is from the pricing calculator.
- [ ] The plan fits on one page.

## What this unlocks on your CV

| Skill | Episode | CV section | Example bullet |
|---|---|---|---|
| Capacity planning | 7 | Cloud platforms | Sized a three-tier app from measured memory use |
| Cloud cost estimation | 7 | Cloud platforms | Estimated the monthly cost of a VM with the GCP pricing calculator |
| Service models, regions, zones | 7 | Cloud platforms | Classified services as IaaS, PaaS, or SaaS and chose a region and zone |
| Network planning | 7 | Networking and security | Planned a VPC with one subnet and firewall rules by CIDR |
| RFC1918 and DNS | 7 | Networking and security | Planned a private network and traced a name with `nslookup` |
| Architecture diagramming | 7 | Cloud platforms | Drew an architecture diagram for review |

## Career note

A cloud engineer writes a short design and asks for review before the build. A wrong size or an open port found in review costs nothing. Found after launch, it costs an incident, a bill, or both. The plan is the cheapest place to be wrong.

## Next

Episode 8 creates the VM and logs in with a key. The plan becomes a machine.

## Apply

The verified steps for this episode are in [Act 2, Episode 7](../act2-cloud-engineer.md#episode-7-plan-the-infrastructure) and in `docs/infrastructure-plan.md`. Follow the tasks in order.

<!-- APPLY -->

### What you should see

| After | You should see |
|---|---|
| You measure the stack | Idle use near 100 MB in total. |
| You run `nslookup github.com` | One or more IP addresses. |
| You draw the diagram | Internet, firewall, VPC, subnet, VM, containers, with ports and CIDRs. |
| You use the pricing calculator | A monthly estimate for 2 vCPUs, 2 GB, and 20 GB. |
| You write the plan | A one-page document with all five parts. |

An end-to-end run of this episode passed: the idle stack used about 80 MB, `nslookup github.com` resolved, and the plan was written.
