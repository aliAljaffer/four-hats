output "vm_ip" {
  value = google_compute_instance.taskboard.network_interface[0].access_config[0].nat_ip
}

output "app_url" {
  value = "http://${google_compute_instance.taskboard.network_interface[0].access_config[0].nat_ip}:8080"
}
