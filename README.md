# Jitouch

**Jitouch** adds multi-touch gestures to the MacBook trackpad, Magic Trackpad and Magic Mouse. Use them to switch browser tabs, close and minimize windows, change spaces, draw characters to launch apps, and more.

Jitouch runs on **macOS 10.13 High Sierra and later**, on both Intel and Apple Silicon Macs.

This is a maintained continuation of [JitouchApp/Jitouch](https://github.com/JitouchApp/Jitouch). For the original project and gesture guide, see https://www.jitouch.com/.

## What's new in this version

- Fixes repeated crashes on current macOS caused by gesture overlays drawn from a background thread.
- Fits the preference pane in modern System Settings, with nothing clipped.
- Stops clicks from being swallowed while two fingers rest on the trackpad.
- Stops the page scrolling during three-finger swipes.
- Gesture-triggered keyboard shortcuts keep their modifier keys, and no modifier key stays stuck.
- Signed with a Developer ID and notarized. The Accessibility permission survives updates.

## Installation

1. Download `Jitouch-<version>.prefPane.zip` from the [latest release](../../releases/latest).
2. Unzip it and double-click `Jitouch.prefPane`, then choose whether to install it for all users or only for you.
3. When macOS asks, allow Jitouch in **System Settings → Privacy & Security → Accessibility**.

Jitouch checks for updates on its own and shows what changed before installing one. To check now, choose **Check for Updates…** in the Jitouch menu bar icon or in the About tab of its settings.

## Troubleshooting

**Gestures do nothing.** Jitouch is running but doesn't have the Accessibility permission. Its log (`~/Library/Logs/com.jitouch.Jitouch.log`) says "Could not create CGEventTap".

1. Open **System Settings → Privacy & Security → Accessibility**.
2. Turn Jitouch on. If it isn't listed, click **+** and add `Jitouch.app` from `/Library/PreferencePanes/Jitouch.prefPane/Contents/Resources/` (or `~/Library/PreferencePanes/...` if you installed it only for your user).
3. Restart Jitouch with `killall Jitouch`. It starts again on its own.

If Jitouch was listed but still doesn't work, remove it from the list with **−**, then add it again.

**"Could not load Jitouch preference pane"** right after installing: restart your Mac.

## Building from source

Requires Xcode and a `Developer ID Application` certificate. Without the certificate, see below.

```sh
make test      # regression scripts
make           # build the app and the preference pane into build/
make install   # install into /Library/PreferencePanes and start Jitouch
```

Official releases are built with **Xcode 16.4**, the newest Xcode that can still build for macOS 10.13 (see [`.github/workflows`](.github/workflows)).

Newer Xcode versions can only build for macOS 12 and later. To build with them, or to build without a Developer ID certificate, copy [`Config/Local.xcconfig.example`](Config/Local.xcconfig.example) to `Config/Local.xcconfig` and adjust it. That file is git-ignored.

## Releasing

Releases are automatic. Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/), and every push to `main` that contains a `feat`, `fix`, `perf` or breaking change since the last tag:

1. bumps the version with [Cocogitto](https://docs.cocogitto.io/) (`feat` → minor, `fix`/`perf` → patch, breaking → major), updates `CHANGELOG.md`, commits and tags `v<version>`;
2. builds, signs and notarizes the preference pane;
3. signs the update and writes a [Sparkle](https://sparkle-project.org/) `appcast.xml` whose release notes list the changes since each user's installed version;
4. publishes the zip and `appcast.xml` as a GitHub release. Installed copies read the feed from `releases/latest/download/appcast.xml`.

Other commit types (`chore`, `ci`, `docs`, `build`, `refactor`, `style`, `test`) never trigger a release. To preview the next version, run `cog bump --auto --dry-run`.

The release workflow needs these repository secrets:

- `DEVELOPER_ID_CERTIFICATE_BASE64` and `DEVELOPER_ID_CERTIFICATE_PASSWORD`: the `.p12` export of the Developer ID Application certificate.
- `APPLE_ID`, `APPLE_TEAM_ID` and `APPLE_APP_SPECIFIC_PASSWORD`: used for notarization.
- `SPARKLE_ED_PRIVATE_KEY`: the EdDSA key that signs updates. It matches `SUPublicEDKey` in [`prefpane/Info.plist`](prefpane/Info.plist). Export it with Sparkle's `generate_keys --account jitouch -x <file>`.

To test updates locally, set `JITOUCH_FEED_URL` in `Config/Local.xcconfig` to a local server, then write a feed with `make zip appcast DOWNLOAD_URL_PREFIX=<server URL>/`.

## Credits

- **Supasorn Suwajanakorn** and **Sukolsak Sakshuwong** created Jitouch.
- **Aaron Kollasch** maintained the open-source release.
- **Toni Oriol** is the current maintainer.

Thanks to Cristi Goia, Jack Saunders and twio142, whose fixes are included here, and to everyone credited in the app's About tab.

## License

Copyright (c) Supasorn Suwajanakorn and Sukolsak Sakshuwong. All rights reserved.
Modified work copyright (c) Aaron Kollasch. All rights reserved.
Modified work copyright (c) 2026 Toni Oriol. All rights reserved.

Licensed under the [GNU General Public License v3.0](LICENSE).
