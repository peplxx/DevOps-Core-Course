# Provider / account

variable "yc_folder_id" {
  description = "Yandex Cloud folder_id."
  type        = string
}

# Region / placement
variable "yc_zone" {
  description = "Yandex Cloud zone."
  type        = string
  default     = "ru-central1-a"
}

# Networking
variable "subnet_cidr" {
  description = "Subnet CIDR block."
  type        = string
  default     = "10.10.0.0/24"
}

# SSH access
variable "ssh_username" {
  description = "Linux username to connect via SSH."
  type        = string
  default     = "ubuntu"
}

variable "ssh_public_key_path" {
  description = "SSH public key path."
  type        = string
  default     = "./certs/devops.pub"
}

variable "ssh_private_key_path" {
  description = "SSH private key path."
  type        = string
  default     = "./certs/devops"
}

# Compute instance
variable "instance_name" {
  description = "Compute instance name."
  type        = string
  default     = "lab05-vm"
}

variable "image_family" {
  description = "Ubuntu image family in Yandex Cloud."
  type        = string
  default     = "ubuntu-2404-lts"
}

variable "platform_id" {
  description = "Yandex Compute platform ID."
  type        = string
  default     = "standard-v2"
}

variable "cores" {
  description = "vCPU cores."
  type        = number
  default     = 2
}

variable "core_fraction" {
  description = "vCPU core fraction."
  type        = number
  default     = 20
}

variable "memory_gb" {
  description = "RAM in GB."
  type        = number
  default     = 1
}

# Boot disk
variable "disk_size_gb" {
  description = "Boot disk size in GB."
  type        = number
  default     = 15
}

variable "disk_type" {
  description = "Boot disk type (e.g. network-hdd or network-ssd)."
  type        = string
  default     = "network-hdd"
}

# Common labels / tags
variable "labels" {
  description = "Common labels for resources."
  type        = map(string)

  default = {
    lab = "lab05"
    iac = "terraform"
  }
}
