BUILD_DIR := build
APP := $(BUILD_DIR)/app/Build/Products/Release/Jitouch.app
PANE := $(BUILD_DIR)/pane/Build/Products/Release/Jitouch.prefPane
ZIP := $(BUILD_DIR)/Jitouch.prefPane.zip
INSTALL_DIR := /Library/PreferencePanes
XCODEBUILD_FLAGS ?=

VERSION = $(shell sed -n 's/^MARKETING_VERSION = //p' Config/Jitouch.xcconfig)
RELEASE_DIR := $(BUILD_DIR)/release
# Sparkle's command line tools, matching the framework version the app embeds.
SPARKLE_VERSION := 2.9.6
SPARKLE_BIN := $(BUILD_DIR)/sparkle/bin
# EdDSA key that signs updates: the "jitouch" account in the login keychain
# by default, or a file (- reads it from stdin).
ED_KEY_FILE ?=
ED_KEY_FLAGS = $(if $(ED_KEY_FILE),--ed-key-file $(ED_KEY_FILE),--account jitouch)
DOWNLOAD_URL_PREFIX ?= https://github.com/tonioriol/Jitouch/releases/download/v$(VERSION)/

.PHONY: all app pane test zip zip-only appcast install clean

all: pane

app:
	xcodebuild -project jitouch/Jitouch/Jitouch.xcodeproj -scheme Jitouch -configuration Release -destination 'generic/platform=macOS' \
		-derivedDataPath $(BUILD_DIR)/app $(XCODEBUILD_FLAGS) build

pane: app
	rm -rf prefpane/Jitouch.app
	ditto $(APP) prefpane/Jitouch.app
	xcodebuild -project prefpane/Jitouch.xcodeproj -scheme Jitouch -configuration Release -destination 'generic/platform=macOS' \
		-derivedDataPath $(BUILD_DIR)/pane $(XCODEBUILD_FLAGS) build
	codesign --verify --deep --strict $(PANE)

test:
	python3 scripts/test-window-threading.py
	python3 scripts/test-prefpane-layout.py --widths 602,668,760

zip: pane zip-only

zip-only:
	rm -f $(ZIP)
	ditto -c -k --keepParent $(PANE) $(ZIP)

# Sparkle feed for the zipped pane, with the release notes since 2.83.0
# embedded. The release attaches both files to the GitHub release.
appcast: $(SPARKLE_BIN)/generate_appcast
	rm -rf $(RELEASE_DIR)
	mkdir -p $(RELEASE_DIR)
	cp $(ZIP) $(RELEASE_DIR)/Jitouch-$(VERSION).prefPane.zip
	scripts/release-notes.sh > $(RELEASE_DIR)/Jitouch-$(VERSION).prefPane.html
	$(SPARKLE_BIN)/generate_appcast $(ED_KEY_FLAGS) --embed-release-notes \
		--download-url-prefix "$(DOWNLOAD_URL_PREFIX)" \
		--link https://github.com/tonioriol/Jitouch $(RELEASE_DIR)

$(SPARKLE_BIN)/generate_appcast:
	mkdir -p $(BUILD_DIR)/sparkle
	curl -fsSL https://github.com/sparkle-project/Sparkle/releases/download/$(SPARKLE_VERSION)/Sparkle-$(SPARKLE_VERSION).tar.xz \
		| tar -xJf - -C $(BUILD_DIR)/sparkle ./bin

install: pane
	-killall Jitouch
	sudo rm -rf $(INSTALL_DIR)/Jitouch.prefPane
	sudo ditto $(PANE) $(INSTALL_DIR)/Jitouch.prefPane
	open $(INSTALL_DIR)/Jitouch.prefPane/Contents/Resources/Jitouch.app

clean:
	rm -rf $(BUILD_DIR) prefpane/Jitouch.app
