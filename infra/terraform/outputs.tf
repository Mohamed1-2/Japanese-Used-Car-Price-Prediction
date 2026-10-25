output "api_url" {
  value = "${var.certificate_arn == null ? "http" : "https"}://${coalesce(var.public_hostname, aws_lb.api.dns_name)}"
}

output "artifact_bucket" {
  value = aws_s3_bucket.model_artifacts.id
}

output "model_s3_uri" {
  value = "s3://${aws_s3_bucket.model_artifacts.id}/${var.model_object_key}"
}

output "ui_options_s3_uri" {
  value = "s3://${aws_s3_bucket.model_artifacts.id}/${var.ui_options_object_key}"
}

output "ecr_repository" {
  value = aws_ecr_repository.api.name
}

output "ecr_repository_url" {
  value = aws_ecr_repository.api.repository_url
}

output "ecs_cluster" {
  value = aws_ecs_cluster.main.name
}

output "ecs_service" {
  value = aws_ecs_service.api.name
}

output "ecs_task_family" {
  value = aws_ecs_task_definition.api.family
}

output "github_actions_role_arn" {
  value = aws_iam_role.github_deploy.arn
}

output "github_repository_variables" {
  value = {
    AWS_REGION      = var.aws_region
    AWS_ROLE_ARN    = aws_iam_role.github_deploy.arn
    ECR_REPOSITORY  = aws_ecr_repository.api.name
    ECS_CLUSTER     = aws_ecs_cluster.main.name
    ECS_SERVICE     = aws_ecs_service.api.name
    ECS_TASK_FAMILY = aws_ecs_task_definition.api.family
    ECS_CONTAINER   = "api"
    API_HEALTH_URL  = "${var.certificate_arn == null ? "http" : "https"}://${coalesce(var.public_hostname, aws_lb.api.dns_name)}/health"
  }
}
