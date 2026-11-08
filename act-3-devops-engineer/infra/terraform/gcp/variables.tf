variable "project_id" {
  description = "Your GCP project ID"
  type        = string
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "zone" {
  type    = string
  default = "us-central1-a"
}

variable "machine_type" {
  type    = string
  default = "e2-small"
}

variable "ssh_public_key" {
  description = "Contents of your public key file"
  type        = string
}

variable "ssh_user" {
  type    = string
  default = "student"
}

variable "allowed_ssh_cidr" {
  description = "Your public IP in CIDR form, for example 203.0.113.7/32"
  type        = string
}
