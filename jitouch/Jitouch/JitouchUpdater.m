//
//  JitouchUpdater.m
//  Jitouch
//
//  Jitouch ships as Jitouch.prefPane with this app at
//  Contents/Resources/Jitouch.app. The app runs all the time, so it hosts the
//  updater, but the bundle Sparkle replaces is the whole preference pane: its
//  Info.plist holds the version, SUFeedURL and SUPublicEDKey. After installing,
//  Sparkle relaunches this app from the updated pane.
//

#import "JitouchUpdater.h"
#import <Sparkle/Sparkle.h>

@interface JitouchUpdater () <SPUUpdaterDelegate, SPUStandardUserDriverDelegate>
@end

@implementation JitouchUpdater {
    SPUStandardUserDriver *userDriver;
    SPUUpdater *updater;
}

+ (instancetype)updaterForEnclosingPreferencePane {
    // <pane>.prefPane/Contents/Resources/Jitouch.app -> <pane>.prefPane
    NSString *panePath = [[[[[NSBundle mainBundle] bundlePath]
                            stringByDeletingLastPathComponent]
                           stringByDeletingLastPathComponent]
                          stringByDeletingLastPathComponent];
    if (![[panePath pathExtension] isEqualToString:@"prefPane"]) {
        NSLog(@"Not running from a preference pane; updates are disabled.");
        return nil;
    }
    NSBundle *pane = [NSBundle bundleWithPath:panePath];
    if (pane == nil) {
        return nil;
    }
    return [[[self alloc] initWithHostBundle:pane] autorelease];
}

- (instancetype)initWithHostBundle:(NSBundle *)hostBundle {
    self = [super init];
    if (self) {
        userDriver = [[SPUStandardUserDriver alloc] initWithHostBundle:hostBundle delegate:self];
        updater = [[SPUUpdater alloc] initWithHostBundle:hostBundle
                                       applicationBundle:[NSBundle mainBundle]
                                              userDriver:userDriver
                                                delegate:self];
        NSError *error = nil;
        if (![updater startUpdater:&error]) {
            NSLog(@"Failed to start the updater: %@", error);
            [self release];
            return nil;
        }
    }
    return self;
}

- (IBAction)checkForUpdates:(id)sender {
    [updater checkForUpdates];
}

- (BOOL)validateMenuItem:(NSMenuItem *)item {
    if ([item action] == @selector(checkForUpdates:)) {
        return [updater canCheckForUpdates];
    }
    return YES;
}

#pragma mark - SPUUpdaterDelegate

// Sparkle quits Jitouch before installing and relaunches it afterwards.
// Launch agents written by Jitouch 2.83 and older use KeepAlive=true, so
// launchd restarts Jitouch on its own after the quit; a Sparkle relaunch would
// then start a second copy. Newer agents only restart Jitouch after a crash.
- (BOOL)updaterShouldRelaunchApplication:(SPUUpdater *)updater {
    NSString *path = [@"~/Library/LaunchAgents/com.jitouch.Jitouch.plist" stringByStandardizingPath];
    id keepAlive = [[NSDictionary dictionaryWithContentsOfFile:path] objectForKey:@"KeepAlive"];
    return !([keepAlive isKindOfClass:[NSNumber class]] && [keepAlive boolValue]);
}

#pragma mark - SPUStandardUserDriverDelegate

// Jitouch has no Dock icon or windows, so an update alert from a scheduled
// check would open behind other apps. Bring it to the front instead.
- (BOOL)supportsGentleScheduledUpdateReminders {
    return YES;
}

- (void)standardUserDriverWillHandleShowingUpdate:(BOOL)handleShowingUpdate
                                        forUpdate:(SUAppcastItem *)update
                                            state:(SPUUserUpdateState *)state {
    [NSApp activateIgnoringOtherApps:YES];
}

- (void)dealloc {
    [updater release];
    [userDriver release];
    [super dealloc];
}

@end
