---
name: findmy
description: "Track Apple devices/AirTags via FindMy.app on macOS."
---

# Find My (Apple)

Track Apple devices and AirTags via the FindMy.app on macOS. Since Apple doesn't
provide a CLI for FindMy, this skill uses AppleScript to open the app and
screen capture to read device locations.

## Prerequisites

- **macOS** with Find My app and iCloud signed in
- Devices/AirTags already registered in Find My
- Screen Recording permission for terminal (System Settings → Privacy → Screen Recording)
- **Optional but recommended**: Install `peekaboo` for better UI automation:
  `brew install steipete/tap/peekaboo`

## When to Use

- User asks "where is my [device/cat/keys/bag]?"
- Tracking AirTag locations
- Checking device locations (iPhone, iPad, Mac, AirPods)
- Monitoring pet or item movement over time (AirTag patrol routes)

## Method 1: AppleScript + Screenshot (Basic)

### Open FindMy and Navigate

```bash
# Open Find My app
osascript -e 'tell application "FindMy" to activate'

# Wait for it to load
sleep 3

# Take a screenshot in a private temporary directory
FINDMY_CAPTURE_DIR=$(mktemp -d)
chmod 700 "$FINDMY_CAPTURE_DIR"
screencapture -w -o "$FINDMY_CAPTURE_DIR/findmy.png"
```

Then inspect `$FINDMY_CAPTURE_DIR/findmy.png` with the current agent's available local-image
viewer. Ask: "What devices/items are shown and what are their locations?" If
the runtime cannot inspect local images, stop and ask the user to attach the
screenshot rather than inventing a location.

After inspection, delete the sensitive capture unless the user explicitly asks
to retain it:

```bash
rm -r -- "$FINDMY_CAPTURE_DIR"
```

### Switch Between Tabs

```bash
# Switch to Devices tab
osascript -e '
tell application "System Events"
    tell process "FindMy"
        click button "Devices" of toolbar 1 of window 1
    end tell
end tell'

# Switch to Items tab (AirTags)
osascript -e '
tell application "System Events"
    tell process "FindMy"
        click button "Items" of toolbar 1 of window 1
    end tell
end tell'
```

## Method 2: Peekaboo UI Automation (Recommended)

If `peekaboo` is installed, use it for more reliable UI interaction:

```bash
# Create private capture storage for this workflow
FINDMY_CAPTURE_DIR=$(mktemp -d "${TMPDIR:-/tmp}/ispo-findmy.XXXXXX") || exit 1
chmod 700 "$FINDMY_CAPTURE_DIR"

# Open Find My
osascript -e 'tell application "FindMy" to activate'
sleep 3

# Capture and annotate the UI
peekaboo see --app "FindMy" --annotate --path "$FINDMY_CAPTURE_DIR/findmy-ui.png"

# Click on a specific device/item by element ID
peekaboo click --on B3 --app "FindMy"

# Capture the detail view
peekaboo image --app "FindMy" --path "$FINDMY_CAPTURE_DIR/findmy-detail.png"
```

Then inspect `$FINDMY_CAPTURE_DIR/findmy-detail.png` with the current agent's available
local-image viewer. Extract only address or coordinates that are visibly
present.

Delete `$FINDMY_CAPTURE_DIR` after inspection unless the user explicitly asks
to retain the screenshots.

## Workflow: Track AirTag Location Over Time

For monitoring an AirTag (e.g., tracking a cat's patrol route):

```bash
# Create private capture storage for this bounded tracking session
FINDMY_CAPTURE_DIR=$(mktemp -d "${TMPDIR:-/tmp}/ispo-findmy.XXXXXX") || exit 1
chmod 700 "$FINDMY_CAPTURE_DIR"

# 1. Open FindMy to Items tab
osascript -e 'tell application "FindMy" to activate'
sleep 3

# 2. Click on the AirTag item (stay on page — AirTag only updates when page is open)

# 3. Periodically capture for the user-approved duration and interval
TRACK_MINUTES=30
INTERVAL_SECONDS=300
DEADLINE=$(( $(date +%s) + TRACK_MINUTES * 60 ))
while [ "$(date +%s)" -lt "$DEADLINE" ]; do
    screencapture -w -o "$FINDMY_CAPTURE_DIR/findmy-$(date +%H%M%S).png"
    sleep "$INTERVAL_SECONDS"
done
```

Analyze each screenshot with vision to extract coordinates, then compile a route.
Delete the private capture directory immediately after the route is compiled
unless the user explicitly requested retention.

## Limitations

- FindMy has **no CLI or API** — must use UI automation
- AirTags only update location while the FindMy page is actively displayed
- Location accuracy depends on nearby Apple devices in the FindMy network
- Screen Recording permission required for screenshots
- AppleScript UI automation may break across macOS versions

## Rules

1. Keep FindMy app in the foreground when tracking AirTags (updates stop when minimized)
2. Use the runtime's available local-image viewer to read screenshot content;
   if none is available, ask the user to attach the image
3. For ongoing tracking explicitly requested by the user, agree on duration and
   interval before creating any scheduled job
4. Location screenshots are sensitive: get explicit approval before ongoing
   monitoring, keep captures private, and never track another person without
   their knowledge and consent
5. Delete captures after inspection unless the user explicitly requests retention
6. Respect privacy — only track devices/items the user owns
