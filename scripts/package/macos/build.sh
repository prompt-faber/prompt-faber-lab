#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-0.1.0}"
OUTDIR="${2:-$(pwd)/dist}"

require() {
  command -v "$1" >/dev/null 2>&1 || { echo "Comando obrigatório não encontrado: $1" >&2; exit 1; }
}

require python3
require xcodebuild
require codesign
require pkgbuild
require productbuild
require hdiutil

python3 -m ensurepip --upgrade >/dev/null 2>&1 || true

VENV="$(pwd)/scripts/package/macos/.venv"
if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
fi

PY="$VENV/bin/python"
"$PY" -m pip install -U pip wheel setuptools >/dev/null
"$PY" -m pip install -e ".[packaging]" >/dev/null

BUILD_DIR="$(pwd)/build/pyinstaller-macos"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

"$PY" -m PyInstaller --clean --noconfirm --onedir --name "PromptFaberLab" --distpath "$BUILD_DIR" -m promptlab >/dev/null

APP_DIR="$BUILD_DIR/PromptFaberLab"
mkdir -p "$OUTDIR"

IDENTITY="${PFL_MACOS_SIGN_IDENTITY:-}"
if [ -n "$IDENTITY" ]; then
  codesign --force --deep --options runtime --sign "$IDENTITY" "$APP_DIR" >/dev/null
fi

PKGROOT="$(pwd)/build/pkgroot"
rm -rf "$PKGROOT"
mkdir -p "$PKGROOT/usr/local/bin"
cp "$APP_DIR/PromptFaberLab" "$PKGROOT/usr/local/bin/prompt-faber-lab" 2>/dev/null || true
if [ ! -f "$PKGROOT/usr/local/bin/prompt-faber-lab" ]; then
  cp "$APP_DIR/PromptFaberLab" "$PKGROOT/usr/local/bin/prompt-faber-lab"
fi

PKG="$OUTDIR/PromptFaberLab-$VERSION-macos.pkg"
pkgbuild --root "$PKGROOT" --identifier "com.promptfaber.lab" --version "$VERSION" "$PKG" >/dev/null

DMG="$OUTDIR/PromptFaberLab-$VERSION-macos.dmg"
TMP_DMG="$(pwd)/build/tmp.dmg"
rm -f "$TMP_DMG" "$DMG"

DMG_DIR="$(pwd)/build/dmg"
rm -rf "$DMG_DIR"
mkdir -p "$DMG_DIR"
cp "$PKG" "$DMG_DIR/"

hdiutil create -fs HFS+ -srcfolder "$DMG_DIR" -volname "PromptFaberLab" "$DMG" >/dev/null

echo "OK: pacotes gerados em $OUTDIR"
