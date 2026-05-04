#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-0.1.0}"
OUTDIR="${2:-$(pwd)/dist}"

require() {
  command -v "$1" >/dev/null 2>&1 || { echo "Comando obrigatório não encontrado: $1" >&2; exit 1; }
}

require python3

python3 -m ensurepip --upgrade >/dev/null 2>&1 || true

VENV="$(pwd)/scripts/package/linux/.venv"
if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
fi

PY="$VENV/bin/python"
"$PY" -m pip install -U pip wheel setuptools >/dev/null
"$PY" -m pip install -e ".[packaging]" >/dev/null

BUILD_DIR="$(pwd)/build/pyinstaller"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

"$PY" -m PyInstaller --clean --noconfirm --onefile --name "prompt-faber-lab" --distpath "$BUILD_DIR" -m promptlab >/dev/null

BIN="$BUILD_DIR/prompt-faber-lab"
if [ ! -f "$BIN" ]; then
  echo "Falha ao gerar binário: $BIN" >&2
  exit 1
fi

mkdir -p "$OUTDIR"
cp "$BIN" "$OUTDIR/prompt-faber-lab-$VERSION-linux-x64"

NFPM="$(pwd)/build/tools/nfpm"
mkdir -p "$(pwd)/build/tools"
if [ ! -x "$NFPM" ]; then
  require curl
  ARCH="$(uname -m)"
  case "$ARCH" in
    x86_64) NFPM_ARCH="amd64" ;;
    aarch64) NFPM_ARCH="arm64" ;;
    *) echo "Arquitetura não suportada para nfpm: $ARCH" >&2; exit 1 ;;
  esac
  curl -fsSL "https://github.com/goreleaser/nfpm/releases/latest/download/nfpm_Linux_${NFPM_ARCH}.tar.gz" -o "$(pwd)/build/tools/nfpm.tar.gz"
  tar -xzf "$(pwd)/build/tools/nfpm.tar.gz" -C "$(pwd)/build/tools"
  chmod +x "$NFPM"
fi

export PFL_VERSION="$VERSION"
export PFL_BIN="$OUTDIR/prompt-faber-lab-$VERSION-linux-x64"
export PFL_OUTDIR="$OUTDIR"

"$NFPM" pkg --packager deb --config scripts/package/linux/nfpm.yaml >/dev/null
"$NFPM" pkg --packager rpm --config scripts/package/linux/nfpm.yaml >/dev/null

APPDIR="$(pwd)/build/appimage/AppDir"
rm -rf "$(pwd)/build/appimage"
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/share/applications"
cp "$BIN" "$APPDIR/usr/bin/prompt-faber-lab"
cat > "$APPDIR/usr/share/applications/prompt-faber-lab.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Prompt Faber Lab
Exec=prompt-faber-lab
Terminal=true
Categories=Development;
EOF

APPIMAGETOOL="$(pwd)/build/tools/appimagetool"
if [ ! -x "$APPIMAGETOOL" ]; then
  require curl
  curl -fsSL "https://github.com/AppImage/AppImageKit/releases/latest/download/appimagetool-x86_64.AppImage" -o "$APPIMAGETOOL"
  chmod +x "$APPIMAGETOOL"
fi

"$APPIMAGETOOL" "$APPDIR" "$OUTDIR/PromptFaberLab-$VERSION-x86_64.AppImage" >/dev/null || true

echo "OK: pacotes gerados em $OUTDIR"
