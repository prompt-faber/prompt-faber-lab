param(
  [Parameter(Mandatory=$false)]
  [string]$Version = "0.1.0",

  [Parameter(Mandatory=$false)]
  [string]$OutDir = "$(Join-Path (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')) 'dist')",

  [Parameter(Mandatory=$false)]
  [switch]$BuildMsi
)

$ErrorActionPreference = "Stop"

function Require-Command([string]$Name) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "Comando obrigatório não encontrado: $Name"
  }
}

Require-Command "python"

python -m ensurepip --upgrade | Out-Null

$venv = Join-Path $PSScriptRoot ".venv"
if (-not (Test-Path $venv)) {
  python -m venv $venv
}

$py = Join-Path $venv "Scripts\python.exe"
& $py -m pip install -U pip wheel setuptools | Out-Null
& $py -m pip install -e ".[packaging]" | Out-Null

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
Push-Location $repoRoot
try {
  $dist = Join-Path $repoRoot "build\pyinstaller"
  if (Test-Path $dist) { Remove-Item -Recurse -Force $dist }
  New-Item -ItemType Directory -Force -Path $dist | Out-Null

  & $py -m PyInstaller `
    --clean `
    --noconfirm `
    --onefile `
    --name "PromptFaberLab" `
    --distpath $dist `
    -m promptlab | Out-Null

  $exePath = Join-Path $dist "PromptFaberLab.exe"
  if (-not (Test-Path $exePath)) {
    throw "Falha ao gerar o binário: $exePath"
  }

  New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
  Copy-Item $exePath (Join-Path $OutDir "PromptFaberLab-$Version-windows-x64.exe") -Force
  $finalExe = (Join-Path $OutDir "PromptFaberLab-$Version-windows-x64.exe")

  $signtool = Get-Command "signtool.exe" -ErrorAction SilentlyContinue
  if ($signtool -and $env:PFL_WINDOWS_PFX_PATH -and $env:PFL_WINDOWS_PFX_PASSWORD) {
    & signtool.exe sign /f $env:PFL_WINDOWS_PFX_PATH /p $env:PFL_WINDOWS_PFX_PASSWORD /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 $finalExe | Out-Null
  }

  $nsis = Join-Path $repoRoot "scripts\package\windows\PromptFaberLab.nsi"
  if (Test-Path $nsis -and (Get-Command "makensis" -ErrorAction SilentlyContinue)) {
    $env:PFL_VERSION = $Version
    $env:PFL_EXE = $finalExe
    $env:PFL_OUTDIR = $OutDir
    makensis $nsis | Out-Null

    $setupExe = (Join-Path $OutDir "PromptFaberLab-$Version-setup.exe")
    if (Test-Path $setupExe -and $signtool -and $env:PFL_WINDOWS_PFX_PATH -and $env:PFL_WINDOWS_PFX_PASSWORD) {
      & signtool.exe sign /f $env:PFL_WINDOWS_PFX_PATH /p $env:PFL_WINDOWS_PFX_PASSWORD /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 $setupExe | Out-Null
    }
  }

  if ($BuildMsi) {
    $wixCandle = Get-Command "candle.exe" -ErrorAction SilentlyContinue
    $wixLight = Get-Command "light.exe" -ErrorAction SilentlyContinue
    if (-not $wixCandle -or -not $wixLight) {
      throw "WiX Toolset (candle.exe/light.exe) não encontrado para gerar MSI."
    }

    $wxs = Join-Path $repoRoot "scripts\package\windows\wix\Product.wxs"
    $wixOut = Join-Path $repoRoot "build\wix"
    if (Test-Path $wixOut) { Remove-Item -Recurse -Force $wixOut }
    New-Item -ItemType Directory -Force -Path $wixOut | Out-Null

    $wixObj = Join-Path $wixOut "Product.wixobj"
    candle.exe -ext WixUIExtension -dVersion=$Version -dSourceExe=$exePath -out $wixObj $wxs | Out-Null
    $msiPath = Join-Path $OutDir "PromptFaberLab-$Version-windows-x64.msi"
    light.exe -ext WixUIExtension -out $msiPath $wixObj | Out-Null
    if (Test-Path $msiPath -and $signtool -and $env:PFL_WINDOWS_PFX_PATH -and $env:PFL_WINDOWS_PFX_PASSWORD) {
      & signtool.exe sign /f $env:PFL_WINDOWS_PFX_PATH /p $env:PFL_WINDOWS_PFX_PASSWORD /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 $msiPath | Out-Null
    }
  }
} finally {
  Pop-Location
}
