resource "google_compute_network" "taskboard" {
  name                    = "taskboard"
  auto_create_subnetworks = true
}

resource "google_compute_firewall" "ssh" {
  name          = "taskboard-allow-ssh"
  network       = google_compute_network.taskboard.name
  source_ranges = [var.allowed_ssh_cidr]
  target_tags   = ["taskboard"]

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
}

resource "google_compute_firewall" "web" {
  name          = "taskboard-allow-web"
  network       = google_compute_network.taskboard.name
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["taskboard"]

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }
}

resource "google_compute_instance" "taskboard" {
  name         = "taskboard"
  machine_type = var.machine_type
  tags         = ["taskboard"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2404-lts-amd64"
      size  = 20
    }
  }

  network_interface {
    network = google_compute_network.taskboard.name
    access_config {}
  }

  metadata = {
    ssh-keys = "${var.ssh_user}:${var.ssh_public_key}"
  }
}
