variable "aws_region" {
  description = "AWS region to deploy resources"
  type = string
  default = "us-east-1"
}

variable "project_name" {
  description = "Project name used to name resources"
  type        = string
  default     = "quantsignal"
}

variable "eks_cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "quantsignal-cluster"
}

variable "eks_node_instance_type" {
  description = "EC2 instance type for EKS nodes"
  type        = string
  default     = "t3.small"
}

variable "eks_node_desired_size" {
  description = "Desired number of nodes"
  type        = number
  default     = 1
}

variable "eks_node_min_size" {
  description = "Minimum number of nodes"
  type        = number
  default     = 1
}

variable "eks_node_max_size" {
  description = "Maximum number of nodes"
  type        = number
  default     = 1
}