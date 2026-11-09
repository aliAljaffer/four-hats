# ALL-26: Build Your CV

**Finale** · Focus: Overview · About 18 to 21 minutes

You started this course with a degree and no job yet. You finish it with four roles practiced, a GitHub project you own, and proof for every line you are about to write. Today that proof becomes a CV.

| | |
|---|---|
| You need | At least one act complete, with its skills ledger rows filled in |
| You build | A built CV at `cv/template.pdf`, a polished GitHub profile, and one short talk track per role you practiced |
| Done when | The PDF opens as one clean page, every skill matches ledger proof, no placeholders remain, the repo is pinned on your profile, and you can say each talk track in about thirty seconds |

## What you will be able to do

- Turn skills ledger rows into CV bullets.
- Build the CV from `cv/template.tex` with a Docker LaTeX image.
- Polish a GitHub profile so it backs up the CV.
- Prepare a short talk track for each role you practiced.

## Before you start

- At least one act complete. The CV only lists what you practiced.
- `cv/skills-ledger.md` filled in for the acts you completed. Each act stands on its own, so you can start at any act and use only those rows.
- A GitHub profile and the project repository in a state you are willing to share.

## Ledger rows become bullets

Open `cv/skills-ledger.md`. Do not start from a blank page. The ledger already lists every skill you can claim, with the episode where you practiced it, the CV section it belongs in, the proof you kept in your repository, and an example bullet for each row. Only use the acts you completed. A student who finished Act 1 can send a CV that night. A student who finished Act 4 uses rows from all four acts. The ledger makes that scope visible before you touch the template.

Each row gives you the proof behind the claim:

| Column | What it tells you |
|---|---|
| Episode | Where you practiced it, so you can point to proof in an interview |
| Proof | The file or result you kept in your repository |
| CV section | The heading in `cv/template.tex` where the skill belongs |
| Example bullet | A starting point, not a copy-paste |

The ledger is built for review. If an interviewer asks about a line on your CV, you can answer with the episode and the file, not with a vague memory. Keep the proof with the row while you fill the template.

## Fill in the template

`cv/template.tex` already has the right section headings. They match the ledger's CV section column. The technical skills part lists seven headings:

- Cloud Platforms
- Containers & Orchestration
- Infrastructure as Code
- CI/CD & Automation
- Monitoring & Observability
- Programming & Scripting
- Networking & Security
- Operating Systems

Copy each practiced skill from the ledger into the matching section. Keep the tool names. Drop the ones you did not practice. A template with seven empty headings invites noise. A template with only the sections your proof backs up reads as honest.

Replace the placeholder name, the contact line, and the example job entries with real ones, or delete a section you do not need yet. The template ships with `YOUR NAME` and example bullets of the form `I did X, using Y, which resulted in Z`. Those are scaffolding, not content. No placeholder may remain in the PDF you send. Check the contact line especially: name, city, phone or email, and links to LinkedIn and GitHub. A wrong link costs more than a missing skill.

The CV also has Work Experience, Side Projects, Education, and Certifications sections. Write only what is true. Side Projects is where the task board from this course belongs. Education is your degree. If you have no certifications yet, delete that section rather than leaving an empty heading.

## Build the PDF

LaTeX needs a full install to render a PDF. Installing it on your laptop creates a heavy toolchain that only this step needs. This course runs it as a Docker image instead, the same way it ran Ansible and Terraform. The `latex` service in `tools/compose.yaml` carries the full TeX distribution. You build the CV with one command:

```shell
docker compose -f tools/compose.yaml run --rm latex pdflatex template.tex
```

`cv/template.pdf` appears. Open it and check that the layout did not break. Keep the build in Docker so the setup stays reproducible on macOS or Windows, with no host LaTeX install and no version drift. If a line overflows or a section runs long, shorten the bullet or remove a less important skill. The target is one page. A two-page junior CV asks the reviewer to do extra work for no gain.

### What you should see

| After | You should see |
|---|---|
| You run the LaTeX image | `cv/template.pdf` exists. |
| You open the PDF | One page, with your name and headline. |
| You check the layout | No line overflows the margin. |
| You check the skills | Only skills you can prove remain. |
| The end-to-end run | A one-page PDF of 67,737 bytes. |

Working directory matters. Run the command from `cv/`, or adjust the path, so `template.tex` and `template.pdf` stay together. The E2E run verified this exact path: `pdflatex` produced a one-page `cv/template.pdf`.

## Write strong bullets

Use the ledger form for every bullet: **I did X, using Y, which resulted in Z.**

- X is what you built or changed.
- Y is the tools and methods you used.
- Z is the result. Use a number when you have one. Build time, replica counts, and scan counts beat adjectives.

The ledger bullets are a starting point, not a copy-paste. Adjust them to match what you actually did, especially if you changed anything from the course. A reviewer who has seen the course template will spot word-for-word copies. Your wording should reflect your repo, your commits, and your measurements. If you sized the VM in Episode 7 from a `docker stats` measurement, say the measured numbers. If you tuned the HPA in Episode 15, name the scale you observed. The form holds even when the wording changes. Any skill without proof behind it must be dropped.

## Polish your GitHub profile

A CV line like "Containerized a three-tier app" is a claim. Your GitHub repository is the proof. Three changes make the repository read well to someone who was not in this course.

First, a clear `README.md` at the top. It should say what the app does, how to run it, and what you built in each act. A reviewer should land on the repo and understand the project without reading the course docs.

Second, pull request history that shows real review, not just solo commits. The merged pull requests from Episodes 2, 4, and 6 show branches, review, and merge. That history is evidence that you can work the way a team works. Merge your pull requests before you apply anywhere. A CV with no matching GitHub activity reads as empty, however true the bullets are.

Third, pin the repository on your GitHub profile page. A reviewer can land on the profile and find the project in one click. Add your other projects beside it only if they are as polished. A pinned but unfinished repo works against you.

## Prepare a talk track for each role

An interview asks about a role, not a repository. Prepare one short answer per act you completed: the task, what you built, and one number or result. Four acts means four thirty-second answers. You do not perform all four in one interview. You pick the one that matches the job.

| Act | Headline | Talk track shape |
|---|---|---|
| 1 | Junior Software Engineer | Task board API with tests and CI: what you built, how you tested it, one result |
| 2 | Junior Software Engineer with Cloud and Infrastructure as Code | One-page plan, VM, and Terraform build: size from measurement, one cost or stability result |
| 3 | Junior DevOps Engineer (Kubernetes, CI/CD, Observability) | Kubernetes deployment with GitOps and monitoring: autoscaling or alert result |
| 4 | Junior Cybersecurity Engineer (Penetration Testing and Application Security) | Injection found, fixed, and scanned: one scan result that proves the fix |

Practice each answer out loud. A bullet on a page and a spoken sentence are different skills. You leave this episode with spoken answers ready, not just written ones. Whichever role you choose next, you now have proof, not just a claim.

## Common mistakes

- **Copying every ledger bullet word for word.** Adjust them to match what you actually built. Verbatim text from the course is visible to anyone who knows the course.
- **Leaving placeholder names, emails, or example jobs in `cv/template.tex`.** No `YOUR NAME` and no example bullet may reach a reviewer. Check the built PDF, not only the `.tex` file.
- **Listing a tool you read about but never used.** Only list what the ledger proof backs up. A skill without a file or a result is a risk in interview.
- **Applying with no matching GitHub activity.** Merge your pull requests, write the README, and pin the repo first. An unmerged or empty profile breaks the proof behind the CV.
- **Sending a two-page CV with seven thin sections.** Keep only the sections your proof supports. One page, strong bullets, real links.

## Check your work

- [ ] Every skill on the CV matches a filled row in `cv/skills-ledger.md` from an act you completed.
- [ ] `cv/template.pdf` builds with the Docker LaTeX image and opens as one page.
- [ ] No placeholder text, no example bullets, and no wrong links remain in the PDF.
- [ ] The repository has a clear `README.md`, merged pull requests, and is pinned on your profile.
- [ ] You can deliver one thirty-second talk track per completed act.

## What this unlocks on your CV

| Skill | Episodes | CV section | Example bullet |
|---|---|---|---|
| Technical documentation | 7, 26 | Programming & Scripting | Documented architecture, runbooks, and trade-offs for a multi-tier system |

## Closing

Four careers, one project, one CV. You built a task board, ran it on a VM, moved it to Kubernetes, then found and fixed a real vulnerability in it.

The files for this work are `cv/template.tex` and `cv/skills-ledger.md` in the course repository. Open the ledger, keep only the acts you completed, copy each skill into its matching template section, and build with `docker compose -f tools/compose.yaml run --rm latex pdflatex template.tex`. Check that `cv/template.pdf` is one page and that every claim has proof behind it.

An end-to-end run of this episode passed: `pdflatex` produced `cv/template.pdf` at one page.

If you stop after Act 1, you can send a CV as a Junior Software Engineer. After Act 2, add cloud and infrastructure as code. After Act 3, add Kubernetes, CI/CD, and observability. After Act 4, send as a Junior Cybersecurity Engineer. Pick the headline that matches the job you want, and use the talk track for that act.

That is the course. Good luck.
