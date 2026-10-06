#!/usr/bin/env python3
"""Compile the preference pane nib, load it with stub classes (no Jitouch
settings/launch-agent side effects), resize the pane the way modern System
Settings does (~602pt wide) and verify that every visible control stays inside
its parent and that no non-wrapping label is wider than its frame.

Usage: scripts/test-prefpane-layout.py [--png-dir DIR] [--widths 602,668,760]
"""
import argparse
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
XIB = ROOT / "prefpane/Base.lproj/JitouchPref.xib"

HARNESS = r'''
#import <Cocoa/Cocoa.h>
#import <ImageIO/ImageIO.h>

@interface Stub : NSObject <NSOutlineViewDataSource>
@property (strong) NSWindow *_window;
@end
@implementation Stub
- (void)setValue:(id)v forUndefinedKey:(NSString *)k {}
- (id)valueForUndefinedKey:(NSString *)k { return nil; }
// Valid empty data source so the outline views load.
- (NSInteger)outlineView:(NSOutlineView *)o numberOfChildrenOfItem:(id)i { return 0; }
- (BOOL)outlineView:(NSOutlineView *)o isItemExpandable:(id)i { return NO; }
- (id)outlineView:(NSOutlineView *)o child:(NSInteger)n ofItem:(id)i { return nil; }
- (id)outlineView:(NSOutlineView *)o objectValueForTableColumn:(NSTableColumn *)c byItem:(id)i { return nil; }
@end
@interface ApplicationButton : NSPopUpButton @end
@implementation ApplicationButton @end
@interface GestureTableView : NSOutlineView @end
@implementation GestureTableView @end
@interface ImageAndTextCell : NSTextFieldCell @end
@implementation ImageAndTextCell @end
@interface KeyTextField : NSTextField @end
@implementation KeyTextField @end
@interface LinkTextField : NSTextField @end
@implementation LinkTextField @end
@interface AutoSetDelegate : Stub @end
@implementation AutoSetDelegate @end
@interface JitouchPref : Stub @end
@implementation JitouchPref @end
@interface TrackpadTab : Stub @end
@implementation TrackpadTab @end
@interface MagicMouseTab : Stub @end
@implementation MagicMouseTab @end
@interface RecognitionTab : Stub @end
@implementation RecognitionTab @end

static int failures;

static NSString *label(NSView *v) {
    NSString *t = @"";
    if ([v isKindOfClass:[NSControl class]]) t = [(NSControl *)v stringValue];
    if (![t length] && [v respondsToSelector:@selector(title)]) t = [(id)v title];
    return [NSString stringWithFormat:@"%@ '%@'", NSStringFromClass([v class]), t];
}

static void check(NSView *v) {
    for (NSView *s in [v subviews]) {
        if ([s isKindOfClass:[NSScroller class]] || [s isKindOfClass:[NSClipView class]]) continue;
        NSRect f = [s frame], b = [v bounds];
        if ([s isHidden]) continue;
        BOOL inX = NSMinX(f) >= -0.5 && NSMaxX(f) <= NSMaxX(b) + 0.5;
        BOOL inY = NSMinY(f) >= -0.5 && NSMaxY(f) <= NSMaxY(b) + 0.5;
        if (!inX || !inY) {
            printf("  FAIL outside parent: %s frame=%s parent=%s\n", [label(s) UTF8String],
                   [NSStringFromRect(f) UTF8String], [NSStringFromRect(b) UTF8String]);
            failures++;
        }
        // Pop-up buttons size to their widest menu item, so only check plain buttons.
        if ([s isKindOfClass:[NSButton class]] && ![s isKindOfClass:[NSPopUpButton class]] && [[(NSButton *)s title] length]) {
            CGFloat w = [[(NSButton *)s cell] cellSize].width;
            if (w > f.size.width + 0.5) {
                printf("  FAIL button title clipped: %s needs %.0f has %.0f\n", [label(s) UTF8String], w, f.size.width);
                failures++;
            }
        }
        if ([s isKindOfClass:[NSTextField class]] && ![(NSTextField *)s isEditable]) {
            NSTextFieldCell *c = [(NSTextField *)s cell];
            NSString *str = [c stringValue];
            if ([str length] && ![c wraps]) {
                CGFloat w = [c cellSizeForBounds:NSMakeRect(0, 0, 10000, 10000)].width;
                if (w > f.size.width + 0.5) {
                    printf("  FAIL label clipped: %s needs %.0f has %.0f\n", [label(s) UTF8String], w, f.size.width);
                    failures++;
                }
            } else if ([str length] && [c wraps]) {
                NSSize need = [c cellSizeForBounds:NSMakeRect(0, 0, f.size.width, 10000)];
                if (need.height > f.size.height + 0.5) {
                    printf("  FAIL wrapped label too tall: %s needs %.0f has %.0f\n", [label(s) UTF8String], need.height, f.size.height);
                    failures++;
                }
            }
        }
        // Controls and scroll views lay out their own private subviews; only check views from the nib.
        if ([s isKindOfClass:[NSScrollView class]] || [s isKindOfClass:[NSControl class]]) continue;
        check(s);
    }
}

int main(int argc, char **argv) {
    @autoreleasepool {
        [NSApplication sharedApplication];
        [NSApp setActivationPolicy:NSApplicationActivationPolicyAccessory];
        [NSApp setAppearance:[NSAppearance appearanceNamed:NSAppearanceNameAqua]];
        NSImage *icon = [[NSImage alloc] initWithContentsOfFile:[NSString stringWithUTF8String:argv[argc - 1]]];
        [icon setName:@"jitouchicon"];
        argc--;
        NSString *nibPath = [NSString stringWithUTF8String:argv[1]];
        NSString *pngDir = argc > 2 && strlen(argv[2]) ? [NSString stringWithUTF8String:argv[2]] : nil;
        for (int a = 3; a < argc; a++) {
            CGFloat width = atof(argv[a]);
            Stub *owner = [[JitouchPref alloc] init];
            NSArray *tops = nil;
            NSBundle *nb = [NSBundle bundleWithPath:[nibPath stringByDeletingLastPathComponent]];
            NSNib *nib = [[NSNib alloc] initWithNibNamed:@"JitouchPref" bundle:nb];
            if (![nib instantiateWithOwner:owner topLevelObjects:&tops]) { printf("nib load failed\n"); return 2; }
            NSWindow *win = owner._window;
            [win setAppearance:[NSAppearance appearanceNamed:NSAppearanceNameAqua]];
            [win setBackgroundColor:[NSColor windowBackgroundColor]];
            NSView *main = [win contentView];
            NSTabView *tv = nil;
            for (NSView *s in [main subviews]) if ([s isKindOfClass:[NSTabView class]]) tv = (NSTabView *)s;
            // Emulate System Settings: the pane view is resized to the available width, height unchanged.
            [win setContentSize:NSMakeSize(width, [main frame].size.height)];
            [main setFrameSize:NSMakeSize(width, [main frame].size.height)];
            [win setFrameOrigin:NSMakePoint(100, 100)];
            [win orderFront:nil];
            [win display];
            printf("== width %.0f (nib default %.0f)\n", width, [win frame].size.width);
            for (NSInteger i = 0; i < [tv numberOfTabViewItems]; i++) {
                [tv selectTabViewItemAtIndex:i];
                NSTabViewItem *item = [tv tabViewItemAtIndex:i];
                printf(" tab %s\n", [[item label] UTF8String]);
                check([item view]);
                if (pngDir) {
                    [win display];
                    [[NSRunLoop currentRunLoop] runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.3]];
                    NSBitmapImageRep *rep = [main bitmapImageRepForCachingDisplayInRect:[main bounds]];
                    [main cacheDisplayInRect:[main bounds] toBitmapImageRep:rep];
                    NSString *p = [pngDir stringByAppendingFormat:@"/pane-%.0f-%@.png", width, [item label]];
                    // Flatten onto an opaque white background so viewers that ignore alpha show the labels.
                    size_t pw = [rep pixelsWide], ph = [rep pixelsHigh];
                    CGColorSpaceRef cs = CGColorSpaceCreateWithName(kCGColorSpaceSRGB);
                    CGContextRef cg = CGBitmapContextCreate(NULL, pw, ph, 8, 0, cs, (CGBitmapInfo)kCGImageAlphaNoneSkipLast);
                    CGContextSetRGBFillColor(cg, 1, 1, 1, 1);
                    CGContextFillRect(cg, CGRectMake(0, 0, pw, ph));
                    CGContextDrawImage(cg, CGRectMake(0, 0, pw, ph), [rep CGImage]);
                    CGImageRef flat = CGBitmapContextCreateImage(cg);
                    CGImageDestinationRef dst = CGImageDestinationCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:p], (__bridge CFStringRef)@"public.png", 1, NULL);
                    CGImageDestinationAddImage(dst, flat, NULL);
                    CGImageDestinationFinalize(dst);
                    CFRelease(dst); CGImageRelease(flat); CGContextRelease(cg); CGColorSpaceRelease(cs);
                }
            }
            printf(" bottom bar\n");
            check(main);
        }
        printf("%s (%d failures)\n", failures ? "FAIL" : "PASS", failures);
        return failures ? 1 : 0;
    }
}
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--png-dir", default="")
    ap.add_argument("--widths", default="602,668")
    args = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        res = tmp / "res"
        res.mkdir()
        nib = res / "JitouchPref.nib"
        subprocess.run(["xcrun", "ibtool", "--compile", str(nib), str(XIB)], check=True)
        src = tmp / "harness.m"
        src.write_text(HARNESS)
        exe = tmp / "harness"
        subprocess.run(["xcrun", "clang", "-fobjc-arc", "-Wno-deprecated-declarations", "-framework", "Cocoa", str(src), "-o", str(exe)], check=True)
        if args.png_dir:
            pathlib.Path(args.png_dir).mkdir(parents=True, exist_ok=True)
        cmd = [str(exe), str(nib), args.png_dir] + args.widths.split(",") + [str(ROOT / "prefpane/jitouchicon.icns")]
        r = subprocess.run(cmd)
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
