#!/bin/bash
# Usage: scripts/release-notes.sh > notes.html
#
# Writes the release notes the update window shows: one section per release
# since 2.83.0 (the last release without automatic updates), newest first,
# generated from the Conventional Commits of each release. Sparkle marks the
# section of the installed version, and the style below hides it and every
# older one, so users see what changed since their version.
set -Eeuo pipefail
cd "$(dirname "$0")/.."

cat <<'HTML'
<style>
.sparkle-installed-version, .sparkle-installed-version ~ section { display: none; }
section + section { border-top: 1px solid rgba(128, 128, 128, 0.3); margin-top: 1em; }
h3 { margin-bottom: 0.2em; }
h4 { margin: 0.6em 0 0.2em; }
ul { margin: 0; padding-left: 1.4em; }
</style>
HTML

git tag --list 'v*' --sort=-version:refname | while read -r tag; do
    [[ "$tag" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] || continue
    [[ "$(printf '%s\n' "$tag" v2.83.0 | sort -V | tail -1)" == "$tag" && "$tag" != v2.83.0 ]] || break
    printf '<section data-sparkle-version="%s">\n' "${tag#v}"
    cog changelog --at "$tag" --template scripts/release-notes.tera
    printf '</section>\n'
done
