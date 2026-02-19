output "public_ip" {
  description = "Public IPv4 address of the VM."
  value       = yandex_compute_instance.this.network_interface[0].nat_ip_address
}

output "private_ip" {
  description = "Private IPv4 address of the VM."
  value       = yandex_compute_instance.this.network_interface[0].ip_address
}

output "ssh_command" {
  description = "SSH command to connect to the VM."
  value       = "ssh -i ${var.ssh_private_key_path} ${var.ssh_username}@${yandex_compute_instance.this.network_interface[0].nat_ip_address}"
}
