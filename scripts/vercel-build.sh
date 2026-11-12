#!/usr/bin/env bash
set -euo pipefail

# Match the SDK revision used to build and test this demo locally.
FLUTTER_REVISION=fe71cadf1959268ca5dd545863a195d78c232b74
FLUTTER_DIR="${TMPDIR:-/tmp}/masters-guide-flutter-${FLUTTER_REVISION}"
if [ ! -d "$FLUTTER_DIR/.git" ]; then
  git init "$FLUTTER_DIR"
  git -C "$FLUTTER_DIR" remote add origin https://github.com/flutter/flutter.git
fi
# Flutter derives its SDK version from reachable release tags. A depth-1
# checkout of an untagged commit reports 0.0.0-unknown and breaks pub solving.
# Fetch the known ancestor tag and enough history to reach it (302 commits).
# Run this for existing checkouts too, so retries repair the original cache.
git -C "$FLUTTER_DIR" fetch --depth 1000 origin "$FLUTTER_REVISION" \
  refs/tags/3.27.0-0.0.pre:refs/tags/3.27.0-0.0.pre
git -C "$FLUTTER_DIR" checkout --detach "$FLUTTER_REVISION"
git -C "$FLUTTER_DIR" describe --tags --match '*.*.*' HEAD
rm -f "$FLUTTER_DIR/version" "$FLUTTER_DIR/bin/cache/flutter.version.json"
export PATH="$FLUTTER_DIR/bin:$PATH"
flutter --version
flutter config --no-analytics
flutter pub get
flutter build web --release
