#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-0.1.0}"
OUTDIR="${2:-$(pwd)/dist}"

require() {
  command -v "$1" >/dev/null 2>&1 || { echo "Comando obrigatório não encontrado: $1" >&2; exit 1; }
}

require node
require npm
require java

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
APP="$ROOT/apps/mobile"

mkdir -p "$OUTDIR"

pushd "$APP" >/dev/null
npm ci >/dev/null
npm run build:web >/dev/null

if [ ! -d "android" ]; then
  npx cap add android >/dev/null
fi

npx cap sync android >/dev/null

pushd android >/dev/null

if [ -n "${PFL_ANDROID_KEYSTORE_PATH:-}" ]; then
  cat > keystore.properties <<EOF
storeFile=${PFL_ANDROID_KEYSTORE_PATH}
storePassword=${PFL_ANDROID_KEYSTORE_PASSWORD}
keyAlias=${PFL_ANDROID_KEY_ALIAS}
keyPassword=${PFL_ANDROID_KEY_PASSWORD}
EOF
fi

./gradlew :app:assembleRelease :app:bundleRelease >/dev/null

APK="app/build/outputs/apk/release/app-release.apk"
AAB="app/build/outputs/bundle/release/app-release.aab"

cp "$APK" "$OUTDIR/PromptFaberLab-$VERSION-android.apk"
cp "$AAB" "$OUTDIR/PromptFaberLab-$VERSION-android.aab"

popd >/dev/null
popd >/dev/null

echo "OK: Android APK/AAB em $OUTDIR"
