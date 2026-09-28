variable "aws_region" {
  description = "AWS region for the API infrastructure."
  type        = string
  default     = "ap-northeast-1"
}

variable "project_name" {
  description = "Short project identifier used in AWS resource names."
  type        = string
  default     = "used-car-price"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "prod"
}

variable "existing_artifact_bucket_name" {
  description = "Existing S3 model bucket to adopt during migration. Leave null for a new bucket."
  type        = string
  default     = null
  nullable    = true
}

variable "existing_ecr_repository_name" {
  description = "Existing ECR repository to adopt during migration. Leave null for a new repository."
  type        = string
  default     = null
  nullable    = true
}

variable "existing_log_group_name" {
  description = "Existing CloudWatch log group to adopt during migration. Leave null for a new log group."
  type        = string
  default     = null
  nullable    = true
}

variable "vpc_cidr" {
  type    = string
  default = "10.40.0.0/16"
}

variable "container_port" {
  type    = number
  default = 8000
}

variable "task_cpu" {
  type    = number
  default = 1024
}

variable "task_memory" {
  type    = number
  default = 2048
}

variable "service_enabled" {
  description = "Set true only after the first image has been pushed to ECR."
  type        = bool
  default     = false
}

variable "desired_count" {
  type    = number
  default = 2
}

variable "max_count" {
  type    = number
  default = 6
}

variable "initial_image_tag" {
  description = "Initial ECR tag. The GitHub workflow creates later task revisions."
  type        = string
  default     = "bootstrap"
}

variable "model_object_key" {
  type    = string
  default = "models/fair-price/v1/fair_price_model.joblib"
}

variable "ui_options_object_key" {
  type    = string
  default = "models/fair-price/v1/ui_options.json"
}

variable "model_sha256" {
  description = "Approved model SHA-256 checked before API startup."
  type        = string
  default     = "ed2c5530e5a84cba1d108ce4d283d4424e4214deff9aa8b82f1de618a9eafd3c"

  validation {
    condition     = can(regex("^[0-9a-f]{64}$", var.model_sha256))
    error_message = "model_sha256 must be a lowercase SHA-256 value."
  }
}

variable "cors_origins" {
  description = "Comma-separated browser origins allowed to call the API."
  type        = string
  default     = ""
}

variable "certificate_arn" {
  description = "Optional ACM certificate ARN. When set, HTTP redirects to HTTPS."
  type        = string
  default     = null
  nullable    = true
}

variable "github_owner" {
  type    = string
  default = "Mohamed1-2"
}

variable "github_repository" {
  type    = string
  default = "Japanese-Used-Car-Price-Prediction"
}

variable "github_environment" {
  type    = string
  default = "production"
}

variable "github_oidc_subject" {
  description = "Exact GitHub OIDC sub claim. Set this for organizations that include stable owner and repository IDs in the subject."
  type        = string
  default     = null
  nullable    = true
}

variable "existing_github_oidc_provider_arn" {
  description = "Use an account-level GitHub OIDC provider ARN if one already exists."
  type        = string
  default     = null
  nullable    = true
}
