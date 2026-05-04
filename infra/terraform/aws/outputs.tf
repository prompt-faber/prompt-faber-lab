output "core_ecr_repository_url" {
  value = aws_ecr_repository.core.repository_url
}

output "auth_ecr_repository_url" {
  value = aws_ecr_repository.auth.repository_url
}

output "report_ecr_repository_url" {
  value = aws_ecr_repository.report.repository_url
}

output "alb_dns_name" {
  value = aws_lb.this.dns_name
}
