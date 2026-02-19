## Overview

Lab 04 is about **Infrastructure as Code (IaC)**: provisioning the same infrastructure using two tools (**Terraform** and **Pulumi**) and comparing the approaches.

Infrastructure goal: get a VM (to be used in Lab 05 / Ansible), reachable via SSH and suitable for running a web service over HTTP.

## 1. Cloud Provider & Infrastructure

- **Cloud provider**: Yandex Cloud (YC)
- **Why YC**: accessible from Russia, has small/free-tier configurations, and good documentation.
- **Zone**: `ru-central1-a` (default in configuration)
- **VM size**:
  - Platform: `standard-v2`
  - vCPU: 2, `core_fraction = 20`
  - RAM: 1 GB
  - Boot disk: 15 GB, `network-hdd`
- **Expected cost**: minimal / around free-tier (depends on the account and current YC conditions)

### Resources created

The following resources are created:

- **VPC network**
- **Subnet**: `10.10.0.0/24`
- **Security group / firewall**
  - Ingress:
    - TCP **22** (SSH) — open
    - TCP **80** (HTTP) — open
    - TCP **5000** (app) — open (future labs)
  - Egress: all outbound traffic is allowed
- **Compute instance** (Ubuntu via image family / image id)
- **Public IP** (via NAT on the network interface)

> Security note: SSH is exposed to the internet — access is still key-based, but you should expect brute-force attempts in logs. In real-world setups, it’s better to restrict SSH to your IP.

## 2. Terraform Implementation

- **Terraform directory**: `project/terraform/`
- **Terraform version**: `1.14.0` (from `project/terraform/terraform.tfstate.backup`)
- **Key files**:
  - `terraform.tf` — required providers / version
  - `variables.tf` — input variables
  - `main.tf` — resources (network/subnet/sg/vm)
  - `outputs.tf` — public IP + SSH command outputs

### Config decisions

- Ubuntu image is resolved via a data source by **image family** (`ubuntu-2404-lts`).
- SSH public key is injected via instance metadata (`ssh-keys`).
- NAT is enabled on the VM → a public IP is assigned.

### Last known Terraform outputs (from state backup)

From `project/terraform/terraform.tfstate.backup` (before destroy):

- **Public IP**: `93.77.188.125`
- **Private IP**: `10.10.0.19`
- **SSH command**: `ssh -i ./certs/devops ubuntu@93.77.188.125`

Status note:

- Current `project/terraform/terraform.tfstate` is empty (no resources), which indicates the Terraform infrastructure was destroyed after the above outputs were recorded.

## 3. Pulumi Implementation

- **Pulumi directory**: `project/pulumi/`
- **Language**: TypeScript
- **Pulumi version**: `<run: pulumi version>`

### How it differs from Terraform

- Terraform is declarative (HCL), while Pulumi is imperative / code-driven (TypeScript).
- Pulumi configuration is provided via `pulumi config` (including secrets via `--secret`).
- In the current Pulumi implementation, the VM requires an explicit `imageId`.

### Pulumi stack configuration (dev)

From `project/pulumi/Pulumi.dev.yaml`:

- **Folder ID**: `b1gu5bsqrkm9ij4rosk4`
- **Zone**: `ru-central1-a`
- **Ubuntu imageId**: `fd84kd8dcu6tmnhbeebv`
- **SSH username**: `ubuntu`
- **SSH public key path**: `../terraform/certs/devops.pub`

> The `yandex:token` value is stored as an encrypted secret in the stack config (not committed in plaintext).

## 4. Terraform vs Pulumi Comparison

### Ease of Learning

- **Terraform**: easier to start with; less “code”; purpose-built for IaC.
- **Pulumi**: convenient if you are comfortable with TypeScript/JS, but you need to understand SDK specifics, types, and outputs.

### Code Readability

- **Terraform**: reads well as a “list of resources”.
- **Pulumi**: more flexible (conditions/loops/functions), but infrastructure becomes a full program.

### Debugging

- **Terraform**: often simpler via `plan` and readable diffs.
- **Pulumi**: good IDE/type support, but you must understand `Output<T>` and apply/interpolate patterns.

### Documentation

- **Terraform**: huge ecosystem and many examples.
- **Pulumi**: strong concept documentation, but some providers may be less actively maintained.

### Use Case

- **Terraform**: when you want a de-facto standard, lots of reusable modules, and a single IaC style.
- **Pulumi**: when you need more logic/reuse and want to write IaC in a real programming language.

## 5. Lab 5 Preparation & Cleanup

### VM for Lab 5

- **Keeping VM for Lab 5**: `No` (Terraform resources already destroyed; Pulumi deployment not verified in state)
- **Plan**: recreate a VM using either Terraform or Pulumi right before Lab 5, and keep it running until Lab 5 is completed.

### Cleanup status

- **Terraform**: destroyed (current `terraform.tfstate` has no resources).
- **Pulumi**: no evidence of an applied deployment state in the repository (paste your `pulumi destroy` output if you created resources).

