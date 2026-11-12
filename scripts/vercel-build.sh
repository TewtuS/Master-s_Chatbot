#!/usr/bin/env bash
set -euo pipefail

# Match the SDK revision used to build and test this demo locally.
FLUTTER_REVISION=fe71cadf1959268ca5dd545863a195d78c232b74
FLUTTER_DIR="${TMPDIR:-/tmp}/masters-guide-flutter-${FLUTTER_REVISION}"
if [ ! -d "$FLUTTER_DIR/.git" ]; then
  git init "$FLUTTER_DIR"
  git -C "$FLUTTER_DIR" remote add origin https://github.com/flutter/flutter.git
  git -C "$FLUTTER_DIR" fetch --depth 1 origin "$FLUTTER_REVISION"
  git -C "$FLUTTER_DIR" checkout --detach FETCH_HEAD
fi
export PATH="$FLUTTER_DIR/bin:$PATH"
flutter config --no-analytics
flutter pub get
flutter build web --release
