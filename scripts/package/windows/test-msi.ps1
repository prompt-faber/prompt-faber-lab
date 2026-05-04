param(
  [Parameter(Mandatory=$true)]
  [string]$MsiPath
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $MsiPath)) {
  throw "MSI não encontrado: $MsiPath"
}

Write-Host "Instalando MSI (silencioso)..." -ForegroundColor Cyan
$logInstall = Join-Path $env:TEMP "prompt-faber-lab-install.log"
Start-Process msiexec.exe -Wait -ArgumentList @("/i", "`"$MsiPath`"", "/qn", "/norestart", "/L*v", "`"$logInstall`"")

$installDir = Join-Path ${env:ProgramFiles} "PromptFaberLab"
$exe = Join-Path $installDir "PromptFaberLab.exe"
if (-not (Test-Path $exe)) {
  throw "Executável não encontrado após instalação: $exe"
}

Write-Host "Validando execução (--help)..." -ForegroundColor Cyan
& $exe --help | Out-Null

Write-Host "Desinstalando MSI (silencioso)..." -ForegroundColor Cyan
$logUninstall = Join-Path $env:TEMP "prompt-faber-lab-uninstall.log"
Start-Process msiexec.exe -Wait -ArgumentList @("/x", "`"$MsiPath`"", "/qn", "/norestart", "/L*v", "`"$logUninstall`"")

if (Test-Path $installDir) {
  throw "Diretório ainda existe após desinstalação: $installDir"
}

Write-Host "OK: instalação/desinstalação validada. Logs:" -ForegroundColor Green
Write-Host $logInstall
Write-Host $logUninstall

