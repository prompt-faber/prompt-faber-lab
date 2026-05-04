variable "aws_region" {
  type        = string
  description = "Região AWS."
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Nome base para recursos."
  default     = "promptlab"
}

variable "environment" {
  type        = string
  description = "Ambiente (staging|prod)."
  default     = "staging"
}

variable "db_username" {
  type        = string
  description = "Usuário do Postgres."
  default     = "promptlab"
}

variable "db_password" {
  type        = string
  description = "Senha do Postgres."
  sensitive   = true
}

variable "jwt_secret" {
  type        = string
  description = "Segredo JWT (usar Secret Manager/SSM em produção)."
  sensitive   = true
}
