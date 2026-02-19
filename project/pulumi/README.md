# Pulumi (Lab 04) — Yandex Cloud VM (TypeScript)

- VPC network + subnet
- Security group:
  - SSH **22** from anywhere
  - HTTP **80** from anywhere
  - App port **5000** from anywhere
- Compute instance (Ubuntu image, NAT enabled → public IP)

## Prerequisites

- Node.js + npm
- Pulumi CLI 3.x
- Yandex Cloud auth (token or service account key)

## Configure (bash)

```bash
cd project/pulumi

# Install deps
npm install

# Login backend (Pulumi Cloud is simplest)
pulumi login

# Create/select stack
pulumi stack init dev || pulumi stack select dev

# Provider config
pulumi config set yandex:folderId "<YOUR_FOLDER_ID>"
pulumi config set yandex:zone "ru-central1-a"

# Auth (choose ONE)
# 1) Token (recommended quick start)
pulumi config set --secret yandex:token "<YOUR_YC_TOKEN>"
# 2) Service account key file (JSON)
# pulumi config set --secret yandex:serviceAccountKeyFile "/absolute/path/to/key.json"

# Program config
pulumi config set imageId "<UBUNTU_IMAGE_ID>"
pulumi config set sshUsername "ubuntu"
pulumi config set sshPublicKeyPath "../terraform/certs/devops.pub"
```

## Run (bash)

```bash
cd project/pulumi
pulumi preview
pulumi up

# Outputs
pulumi stack output vmPublicIp
pulumi stack output sshCommand
```

## Cleanup (bash)

```bash
cd project/pulumi
pulumi destroy
```
