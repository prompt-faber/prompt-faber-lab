param(
  [Parameter(Mandatory=$true)]
  [ValidateSet("staging","prod")]
  [string]$Environment,

  [Parameter(Mandatory=$true)]
  [string]$DbPassword,

  [Parameter(Mandatory=$true)]
  [string]$JwtSecret,

  [Parameter(Mandatory=$false)]
  [string]$AwsRegion = "us-east-1"
)

$ErrorActionPreference = "Stop"

$tfDir = Join-Path $PSScriptRoot "..\infra\terraform\aws"
$tfVars = Join-Path $tfDir "$Environment.tfvars"

if (-not (Test-Path $tfVars)) {
  throw "Arquivo tfvars não encontrado: $tfVars"
}

Push-Location $tfDir
try {
  terraform init
  terraform apply -auto-approve `
    -var-file="$tfVars" `
    -var="db_password=$DbPassword" `
    -var="jwt_secret=$JwtSecret" `
    -var="aws_region=$AwsRegion"

  $coreRepo = terraform output -raw core_ecr_repository_url 2>$null
  $authRepo = terraform output -raw auth_ecr_repository_url 2>$null
  $reportRepo = terraform output -raw report_ecr_repository_url 2>$null
  if (-not $coreRepo -or -not $authRepo -or -not $reportRepo) {
    Write-Host "Outputs de ECR não encontrados. Verifique outputs.tf." -ForegroundColor Yellow
    return
  }
} finally {
  Pop-Location
}

Write-Host "Faz login no ECR e publica imagens..." -ForegroundColor Cyan

$accountId = ($coreRepo.Split(".")[0])
aws ecr get-login-password --region $AwsRegion | docker login --username AWS --password-stdin "$accountId.dkr.ecr.$AwsRegion.amazonaws.com"

Push-Location (Join-Path $PSScriptRoot "..")
try {
  docker build -t promptlab-core .
  docker tag promptlab-core "$coreRepo:latest"
  docker push "$coreRepo:latest"

  docker build -t promptlab-auth .
  docker tag promptlab-auth "$authRepo:latest"
  docker push "$authRepo:latest"

  docker build --build-arg PIP_EXTRAS=reports -t promptlab-report .
  docker tag promptlab-report "$reportRepo:latest"
  docker push "$reportRepo:latest"
} finally {
  Pop-Location
}
