locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

data "aws_default_vpc" "this" {}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_default_vpc.this.id]
  }
}

resource "aws_security_group" "alb" {
  name        = "${local.name_prefix}-alb"
  description = "ALB security group"
  vpc_id      = data.aws_default_vpc.this.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs" {
  name        = "${local.name_prefix}-ecs"
  description = "ECS tasks security group"
  vpc_id      = data.aws_default_vpc.this.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "db" {
  name        = "${local.name_prefix}-db"
  description = "Postgres security group"
  vpc_id      = data.aws_default_vpc.this.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_subnet_group" "db" {
  name       = "${local.name_prefix}-db-subnets"
  subnet_ids = data.aws_subnets.default.ids
}

resource "aws_db_instance" "postgres" {
  identifier             = "${local.name_prefix}-postgres"
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = "db.t4g.micro"
  allocated_storage      = 20
  db_name                = var.project_name
  username               = var.db_username
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.db.name
  vpc_security_group_ids = [aws_security_group.db.id]
  skip_final_snapshot    = true
  publicly_accessible    = false
}

resource "aws_ecr_repository" "core" {
  name = "${local.name_prefix}-core"
}

resource "aws_ecr_repository" "auth" {
  name = "${local.name_prefix}-auth"
}

resource "aws_ecr_repository" "report" {
  name = "${local.name_prefix}-report"
}

resource "aws_ecs_cluster" "this" {
  name = "${local.name_prefix}-cluster"
}

resource "aws_lb" "this" {
  name               = "${local.name_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = data.aws_subnets.default.ids
}

resource "aws_lb_target_group" "core" {
  name        = "${local.name_prefix}-core"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = data.aws_default_vpc.this.id
  target_type = "ip"
  health_check {
    path = "/docs"
  }
}

resource "aws_lb_target_group" "auth" {
  name        = "${local.name_prefix}-auth"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = data.aws_default_vpc.this.id
  target_type = "ip"
  health_check {
    path = "/docs"
  }
}

resource "aws_lb_target_group" "report" {
  name        = "${local.name_prefix}-report"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = data.aws_default_vpc.this.id
  target_type = "ip"
  health_check {
    path = "/docs"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.core.arn
  }
}

resource "aws_lb_listener_rule" "auth" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 10

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.auth.arn
  }

  condition {
    path_pattern {
      values = ["/auth/*"]
    }
  }
}

resource "aws_lb_listener_rule" "report" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 20

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.report.arn
  }

  condition {
    path_pattern {
      values = ["/reports/*"]
    }
  }
}

data "aws_iam_policy_document" "ecs_task_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_task_execution" {
  name               = "${local.name_prefix}-ecs-task-exec"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${local.name_prefix}"
  retention_in_days = 14
}

locals {
  database_url = "postgresql+psycopg://${var.db_username}:${var.db_password}@${aws_db_instance.postgres.address}:5432/${var.project_name}"
}

resource "aws_ecs_task_definition" "core" {
  family                   = "${local.name_prefix}-core"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name      = "core"
      image     = "${aws_ecr_repository.core.repository_url}:latest"
      essential = true
      portMappings = [{ containerPort = 8000, hostPort = 8000, protocol = "tcp" }]
      command = ["sh","-c","alembic upgrade head && uvicorn promptlab.services.core.app:app --host 0.0.0.0 --port 8000"]
      environment = [
        { name = "PROMPTLAB_DATABASE_URL", value = local.database_url },
        { name = "PROMPTLAB_JWT_SECRET", value = var.jwt_secret },
        { name = "PROMPTLAB_CORS_ORIGINS", value = "*" },
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "core"
        }
      }
    }
  ])
}

resource "aws_ecs_task_definition" "auth" {
  family                   = "${local.name_prefix}-auth"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name      = "auth"
      image     = "${aws_ecr_repository.auth.repository_url}:latest"
      essential = true
      portMappings = [{ containerPort = 8000, hostPort = 8000, protocol = "tcp" }]
      command = ["sh","-c","alembic upgrade head && uvicorn promptlab.services.auth.app:app --host 0.0.0.0 --port 8000"]
      environment = [
        { name = "PROMPTLAB_DATABASE_URL", value = local.database_url },
        { name = "PROMPTLAB_JWT_SECRET", value = var.jwt_secret },
        { name = "PROMPTLAB_CORS_ORIGINS", value = "*" },
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "auth"
        }
      }
    }
  ])
}

resource "aws_ecs_task_definition" "report" {
  family                   = "${local.name_prefix}-report"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name      = "report"
      image     = "${aws_ecr_repository.report.repository_url}:latest"
      essential = true
      portMappings = [{ containerPort = 8000, hostPort = 8000, protocol = "tcp" }]
      command = ["uvicorn","promptlab.services.report.app:app","--host","0.0.0.0","--port","8000"]
      environment = [
        { name = "PROMPTLAB_JWT_SECRET", value = var.jwt_secret },
        { name = "PROMPTLAB_CORS_ORIGINS", value = "*" },
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "report"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "core" {
  name            = "${local.name_prefix}-core"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.core.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.core.arn
    container_name   = "core"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.http]
}

resource "aws_ecs_service" "auth" {
  name            = "${local.name_prefix}-auth"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.auth.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.auth.arn
    container_name   = "auth"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener_rule.auth]
}

resource "aws_ecs_service" "report" {
  name            = "${local.name_prefix}-report"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.report.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.report.arn
    container_name   = "report"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener_rule.report]
}
