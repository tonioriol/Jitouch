BUILD_DIR := build
APP := $(BUILD_DIR)/app/Build/Products/Release/Jitouch.app
PANE := $(BUILD_DIR)/pane/Build/Products/Release/Jitouch.prefPane
ZIP := $(BUILD_DIR)/Jitouch.prefPane.zip
INSTALL_DIR := /Library/PreferencePanes

.PHONY: all app pane test zip install clean

all: pane

app:
	xcodebuild -project jitouch/Jitouch/Jitouch.xcodeproj -scheme Jitouch -configuration Release \
		-derivedDataPath $(BUILD_DIR)/app build

pane: app
	rm -rf prefpane/Jitouch.app
	ditto $(APP) prefpane/Jitouch.app
	xcodebuild -project prefpane/Jitouch.xcodeproj -scheme Jitouch -configuration Release \
		-derivedDataPath $(BUILD_DIR)/pane build
	codesign --verify --deep --strict $(PANE)

test:
	python3 scripts/test-window-threading.py
	python3 scripts/test-prefpane-layout.py --widths 602,668,760

zip: pane
	rm -f $(ZIP)
	ditto -c -k --keepParent $(PANE) $(ZIP)

install: pane
	-killall Jitouch
	sudo rm -rf $(INSTALL_DIR)/Jitouch.prefPane
	sudo ditto $(PANE) $(INSTALL_DIR)/Jitouch.prefPane
	open $(INSTALL_DIR)/Jitouch.prefPane/Contents/Resources/Jitouch.app

clean:
	rm -rf $(BUILD_DIR) prefpane/Jitouch.app
