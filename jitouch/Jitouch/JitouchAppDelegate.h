//
//  JitouchAppDelegate.h
//  Jitouch
//
//  Copyright 2021 Supasorn Suwajanakorn and Sukolsak Sakshuwong. All rights reserved.
//

#import <Cocoa/Cocoa.h>

@class CursorWindow;
@class Gesture;
@class JitouchUpdater;

@interface JitouchAppDelegate : NSObject <NSApplicationDelegate> {
    NSWindow *window;
    Gesture *gesture;
    NSMenu *theMenu;
    NSStatusItem *theItem;
    JitouchUpdater *updater;
}

@property (assign) IBOutlet NSWindow *window;

- (void)reload;

@end

extern CursorWindow *cursorWindow;
extern CGKeyCode keyMap[128]; // for dvorak support
