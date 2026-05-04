#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-0.1.0}"
OUTDIR="${2:-$(pwd)/dist}"

require() {
  command -v "$1" >/dev/null 2>&1 || { echo "Comando obrigatório não encontrado: $1" >&2; exit 1; }
}

require node
require npm
require xcodebuild

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
APP="$ROOT/apps/mobile"

mkdir -p "$OUTDIR"

pushd "$APP" >/dev/null
npm ci >/dev/null
npm run build:web >/dev/null

if [ ! -d "ios" ]; then
  npx cap add ios >/dev/null
fi

npx cap sync ios >/dev/null

SCHEME="App"
WORKSPACE="ios/App/App.xcworkspace"
ARCHIVE_PATH="$ROOT/build/ios/PromptFaberLab.xcarchive"
EXPORT_PATH="$ROOT/build/ios/export"
mkdir -p "$(dirname "$ARCHIVE_PATH")" "$EXPORT_PATH"

xcodebuild -workspace "$WORKSPACE" -scheme "$SCHEME" -configuration Release -archivePath "$ARCHIVE_PATH" archive >/dev/null

if [ -z "${PFL_IOS_EXPORT_OPTIONS_PLIST:-}" ]; then
  echo "PFL_IOS_EXPORT_OPTIONS_PLIST não definido (necessário para exportar IPA)." >&2
  exit 1
fi

xcodebuild -exportArchive -archivePath "$ARCHIVE_PATH" -exportPath "$EXPORT_PATH" -exportOptionsPlist "$PFL_IOS_EXPORT_OPTIONS_PLIST" >/dev/null

IPA="$(find "$EXPORT_PATH" -maxdepth 1 -name "*.ipa" -print -quit)"
if [ -z "$IPA" ]; then
  echo "IPA não encontrado em $EXPORT_PATH" >&2
  exit 1
fi

cp "$IPA" "$OUTDIR/PromptFaberLab-$VERSION-ios.ipa"
popd >/dev/null

echo "OK: iOS IPA em $OUTDIR"
