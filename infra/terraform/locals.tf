locals {
  name = "${var.project_name}-${var.environment}"

  artifact_bucket_name = var.existing_artifact_bucket_name != null ? var.existing_artifact_bucket_name : "${local.name}-models-${random_id.bucket_suffix[0].hex}"
  ecr_repository_name  = var.existing_ecr_repository_name != null ? var.existing_ecr_repository_name : "${local.name}-api"
  log_group_name       = var.existing_log_group_name != null ? var.existing_log_group_name : "/ecs/${local.name}-api"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  availability_zones = slice(data.aws_availability_zones.available.names, 0, 2)

  github_oidc_provider_arn = var.existing_github_oidc_provider_arn != null ? var.existing_github_oidc_provider_arn : aws_iam_openid_connect_provider.github[0].arn
  github_oidc_subject      = var.github_oidc_subject != null ? var.github_oidc_subject : "repo:${var.github_owner}/${var.github_repository}:environment:${var.github_environment}"
}

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

data "tls_certificate" "github" {
  count = var.existing_github_oidc_provider_arn == null ? 1 : 0
  url   = "https://token.actions.githubusercontent.com"
}

resource "random_id" "bucket_suffix" {
  count       = var.existing_artifact_bucket_name == null ? 1 : 0
  byte_length = 4
}
