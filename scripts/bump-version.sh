#!/bin/bash
# Usage: scripts/bump-version.sh 2.83.0
set -Eeuo pipefail

VERSION="${1#v}"
[[ -z "$(git diff --staged)" ]] || { echo "git has staged changes; will not bump version"; exit 1; }

sed -E -i '' "s/^(MARKETING_VERSION|CURRENT_PROJECT_VERSION) = .*/\1 = $VERSION/" Config/Jitouch.xcconfig
sed -E -i '' "s/\"Version [-0-9A-Za-z.]*\"/\"Version $VERSION\"/" prefpane/Base.lproj/JitouchPref.xib

git add Config/Jitouch.xcconfig prefpane/Base.lproj/JitouchPref.xib
git commit -m "chore: release $VERSION"
git tag -a "v$VERSION" -m "Jitouch $VERSION"
