//
//  JitouchUpdater.h
//  Jitouch
//
//  Checks for and installs updates of the enclosing Jitouch.prefPane with Sparkle.
//

#import <Cocoa/Cocoa.h>

@interface JitouchUpdater : NSObject

// Nil when the app does not run from inside Jitouch.prefPane (e.g. from Xcode),
// because then there is no installed bundle to update.
+ (instancetype)updaterForEnclosingPreferencePane;

- (IBAction)checkForUpdates:(id)sender;

@end
