# Terraform (Lab 04) — Yandex Cloud VM

This folder provisions a small VM in Yandex Cloud for Lab 04 (and can be kept for Lab 05 / Ansible).

## What it creates

- VPC network + subnet
- Security group:
  - SSH **22** from anywhere
  - HTTP **80** from anywhere
- Compute instance (Ubuntu image family, NAT enabled → public IP)

## Prerequisites

- Terraform **1.13+**
- Yandex Cloud account + `folder_id`
- Auth configured for Yandex service provider [link](https://yandex.cloud/ru/docs/iam/concepts/users/service-accounts)
- SSH key pair (public key string)

## Configure variables

Create `terraform/terraform.tfvars` and fill:

```hcl
yc_folder_id     = "..."
yc_zone          = "ru-central1-a"

ssh_username     = "ubuntu"
```

## Run

From repository root:

```bash
terraform init
terraform validate
terraform plan
terraform apply
```

After apply, use the output:

```bash
terraform output -raw ssh_command
```

## Cleanup

```bash
cd terraform
terraform destroy
```

## Notes

- Do **NOT** commit `*.tfstate`, `terraform.tfvars`, service account keys, or any credentials.
- If `image_family = "ubuntu-2404-lts"` is unavailable in your folder/zone, try `ubuntu-2204-lts`.
