#!/usr/bin/env bash
set -euo pipefail
trap 'echo "Flutter build failed at line ${LINENO}: ${BASH_COMMAND}" >&2' ERR

# Clone a tagged stable release: untagged, detached development revisions can
# report 0.0.0-unknown and cause Flutter SDK dependency constraints to fail.
FLUTTER_VERSION=3.29.3
FLUTTER_DIR="${TMPDIR:-/tmp}/masters-guide-flutter-stable-${FLUTTER_VERSION}"
if [ ! -d "$FLUTTER_DIR/.git" ]; then
  git clone --depth 1 --branch "$FLUTTER_VERSION" \
    https://github.com/flutter/flutter.git "$FLUTTER_DIR"
fi
# Refuse a stale or unexpected SDK before using its binaries.
test "$(git -C "$FLUTTER_DIR" describe --tags --exact-match HEAD)" = "$FLUTTER_VERSION"
export PATH="$FLUTTER_DIR/bin:$PATH"
export CI=true
export FLUTTER_SUPPRESS_ANALYTICS=true
# Bootstrap first: a first-ever Flutter invocation can write download progress
# to stdout, which would contaminate the machine-readable JSON below.
flutter config --no-analytics
flutter --version --machine > "$FLUTTER_DIR/verified-version.json"
node -e 'const fs = require("fs"); const v = JSON.parse(fs.readFileSync(process.argv[1], "utf8")); if (v.frameworkVersion !== process.argv[2]) { throw new Error(`Expected Flutter ${process.argv[2]}, got ${v.frameworkVersion}`); } console.log(`Building with Flutter ${v.frameworkVersion}, Dart ${v.dartSdkVersion}`);' \
  "$FLUTTER_DIR/verified-version.json" "$FLUTTER_VERSION"
flutter pub get
flutter build web --release
