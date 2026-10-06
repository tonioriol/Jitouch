#!/usr/bin/env python3
"""Exercise production gesture cleanup with a thread-checking window double."""
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
source = (ROOT / "jitouch/Jitouch/Gesture.m").read_text()


def function(name):
    start = re.search(r"^static \w+ " + re.escape(name) + r"\(", source, re.MULTILINE).start()
    opening = source.index("{", start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end]


harness = r'''
#import <Cocoa/Cocoa.h>
#import <CoreGraphics/CoreGraphics.h>
#include <stdio.h>
#include <stdlib.h>
#define MAGICMOUSE 1
#define MIDDLEBUTTONDOWN 2
struct Finger { float px, py; };
typedef struct Finger Finger;
static int middleClickFlag, magicMouseThreeFingerFlag, simulating;
static int disableHorizontalScroll, quickTabSwitching, simulatingByDevice;
static int cursorImageType, isTrackpadRecognizing, isMouseRecognizing;
static float findTabGroup_lx;
static NSString *command;
static int calls;
@interface CheckedWindow : NSObject
- (void)orderOut:(id)sender;
- (void)clear;
- (void)display;
- (void)setLevel:(NSInteger)level;
- (void)makeKeyAndOrderFront:(id)sender;
@end
@implementation CheckedWindow
- (void)check {
    if (![NSThread isMainThread]) {
        fprintf(stderr, "FAIL: overlay operation on multitouch worker thread\n");
        exit(42);
    }
    calls++;
}
- (void)orderOut:(id)sender { [self check]; }
- (void)clear { [self check]; }
- (void)display { [self check]; }
- (void)setLevel:(NSInteger)level { [self check]; }
- (void)makeKeyAndOrderFront:(id)sender { [self check]; }
@end
static CheckedWindow *cursorWindow, *gestureWindow;
static NSString *commandForGesture(NSString *gesture, int device) { return command; }
static BOOL selectSafariTab(void) { return YES; }
static void dispatchCommand(NSString *gesture, int device) {}
'''
harness += "\n" + "\n".join(function(name) for name in (
    "turnOffMagicMouse", "turnOffCharacters", "gestureMagicMouseThumb"))
harness += r'''
int main(void) {
    @autoreleasepool {
        cursorWindow = [CheckedWindow new];
        gestureWindow = [CheckedWindow new];
        dispatch_semaphore_t finished = dispatch_semaphore_create(0);
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_DEFAULT, 0), ^{
            @autoreleasepool {
                Finger thumb = { .px = 0.1, .py = 0.5 };
                Finger outside = { .px = 0.5, .py = 0.8 };
                // The reported failure: leave the thumb region after activation.
                command = nil;
                gestureMagicMouseThumb(&thumb, 1);
                gestureMagicMouseThumb(&outside, 1);
                // Lift all contacts; then exercise the overlay-display branch.
                gestureMagicMouseThumb(&thumb, 1);
                gestureMagicMouseThumb(NULL, 0);
                command = @"Quick Tab Switching";
                gestureMagicMouseThumb(&thumb, 1);
                gestureMagicMouseThumb(NULL, 0);
                turnOffMagicMouse();
                turnOffCharacters();
                dispatch_semaphore_signal(finished);
            }
        });
        NSDate *deadline = [NSDate dateWithTimeIntervalSinceNow:5];
        while (dispatch_semaphore_wait(finished, DISPATCH_TIME_NOW) != 0) {
            if ([deadline timeIntervalSinceNow] <= 0) return 2;
            [[NSRunLoop mainRunLoop] runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.01]];
        }
        while (calls < 9 && [deadline timeIntervalSinceNow] > 0)
            [[NSRunLoop mainRunLoop] runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.01]];
        if (calls != 9) {
            fprintf(stderr, "FAIL: expected 9 overlay operations, got %d\n", calls);
            return 3;
        }
        printf("PASS: all 9 production overlay operations ran on the main thread\n");
    }
    return 0;
}
'''
with tempfile.TemporaryDirectory(prefix="jitouch-window-test-") as directory:
    path = pathlib.Path(directory)
    (path / "test.m").write_text(harness)
    subprocess.run(["xcrun", "clang", "-fblocks", "-framework", "Cocoa",
                    "-framework", "CoreGraphics", str(path / "test.m"),
                    "-o", str(path / "test")], check=True)
    result = subprocess.run([str(path / "test")])
    raise SystemExit(result.returncode)
