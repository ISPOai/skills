---
name: youtube-transcript
description: Download YouTube video transcripts when user provides a YouTube URL or asks to download/get/fetch a transcript from YouTube. Also use when user wants to transcribe or get captions/subtitles from a YouTube video.
---

# YouTube Transcript Downloader

This skill helps download transcripts (subtitles/captions) from YouTube videos using yt-dlp.

## When to Use This Skill

Activate this skill when the user:
- Provides a YouTube URL and wants the transcript
- Asks to "download transcript from YouTube"
- Wants to "get captions" or "get subtitles" from a video
- Asks to "transcribe a YouTube video"
- Needs text content from a YouTube video

## How It Works

### Priority Order:
1. **Check if yt-dlp is installed** - report the declared prerequisite if missing
2. **List available subtitles** - see what's actually available
3. **Try manual subtitles first** (`--write-sub`) - highest quality
4. **Fallback to auto-generated** (`--write-auto-sub`) - usually available
5. **Last resort: Whisper transcription** - if no subtitles exist (requires user confirmation)
6. **Confirm the download** and show the user where the file is saved
7. **Optionally clean up** the VTT format if the user wants plain text

## Installation Check

**IMPORTANT**: Always check if yt-dlp is installed first:

```bash
which yt-dlp || command -v yt-dlp
```

### If Not Installed

Stop and report the missing declared prerequisite. Do not mutate the user's
Homebrew, apt, or Python environment automatically. If the user asks for setup
help, offer the appropriate command for them to review and run:

**macOS (Homebrew)**:
```bash
brew install yt-dlp
```

**Linux (apt/Debian/Ubuntu)**:
```bash
sudo apt update && sudo apt install -y yt-dlp
```

**Alternative (isolated pipx environment)**:
```bash
pipx install yt-dlp
```

After user-managed installation, verify `yt-dlp --version` before proceeding.

## Check Available Subtitles

**ALWAYS do this first** before attempting to download:

```bash
yt-dlp --list-subs "YOUTUBE_URL"
```

This shows what subtitle types are available without downloading anything. Look for:
- Manual subtitles (better quality)
- Auto-generated subtitles (usually available)
- Available languages

## Download Strategy

### Option 1: Manual Subtitles (Preferred)

Try this first - highest quality, human-created:

```bash
yt-dlp --write-sub --skip-download --output "OUTPUT_NAME" "YOUTUBE_URL"
```

### Option 2: Auto-Generated Subtitles (Fallback)

If manual subtitles aren't available:

```bash
yt-dlp --write-auto-sub --skip-download --output "OUTPUT_NAME" "YOUTUBE_URL"
```

Both commands create a `.vtt` file (WebVTT subtitle format).

## Option 3: Whisper Transcription (Last Resort)

**ONLY use this if both manual and auto-generated subtitles are unavailable.**

### Step 1: Show File Size and Ask for Confirmation

```bash
# Get audio file size estimate
yt-dlp --print "%(filesize,filesize_approx)s" -f "bestaudio" "YOUTUBE_URL"

# Or get duration to estimate
yt-dlp --print "%(duration)s %(title)s" "YOUTUBE_URL"
```

**IMPORTANT**: Display the file size to the user and ask: "No subtitles are available. I can download the audio (approximately X MB) and transcribe it using Whisper. Would you like to proceed?"

**Wait for user confirmation before continuing.**

### Step 2: Check for Whisper Installation

```bash
command -v whisper
```

If it is not installed, stop and report the optional prerequisite. Explain that
`openai-whisper` plus its model download may require several gigabytes. Do not
install it into the ambient Python environment. Continue only after the user
has installed Whisper in a user-managed isolated environment and
`command -v whisper` succeeds.

### Step 3: Download Audio Only

```bash
yt-dlp -x --audio-format mp3 --output "audio_%(id)s.%(ext)s" "YOUTUBE_URL"
```

### Step 4: Transcribe with Whisper

```bash
# Auto-detect language (recommended)
whisper audio_VIDEO_ID.mp3 --model base --output_format vtt

# Or specify language if known
whisper audio_VIDEO_ID.mp3 --model base --language en --output_format vtt
```

**Model Options** (stick to `base` for now):
- `tiny` - fastest, least accurate (~1GB)
- `base` - good balance (~1GB) ← **USE THIS**
- `small` - better accuracy (~2GB)
- `medium` - very good (~5GB)
- `large` - best accuracy (~10GB)

### Step 5: Cleanup

After transcription completes, ask user: "Transcription complete! Would you like me to delete the audio file to save space?"

If yes:
```bash
rm audio_VIDEO_ID.mp3
```

## Getting Video Information

### Extract Video Title (for filename)

```bash
yt-dlp --print "%(title)s" "YOUTUBE_URL"
```

Use this to create meaningful filenames based on the video title. Clean the title for filesystem compatibility:
- Replace `/` with `-`
- Replace special characters that might cause issues
- Consider using sanitized version: `$(yt-dlp --print "%(title)s" "URL" | tr '/' '-' | tr ':' '-')`

## Post-Processing

### Convert to Plain Text (Recommended)

YouTube's auto-generated VTT files contain **duplicate lines** because captions are shown progressively with overlapping timestamps. Always deduplicate when converting to plain text while preserving the original speaking order.

```bash
python3 -c "
import sys, re
seen = set()
with open('transcript.en.vtt', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('WEBVTT') and not line.startswith('Kind:') and not line.startswith('Language:') and '-->' not in line:
            clean = re.sub('<[^>]*>', '', line)
            clean = clean.replace('&amp;', '&').replace('&gt;', '>').replace('&lt;', '<')
            if clean and clean not in seen:
                print(clean)
                seen.add(clean)
" > transcript.txt
```

### Complete Post-Processing with Video Title

```bash
# Get video title
VIDEO_TITLE=$(yt-dlp --print "%(title)s" "YOUTUBE_URL" | tr '/' '_' | tr ':' '-' | tr '?' '' | tr '"' '')

# Find the VTT file
VTT_FILE=$(ls *.vtt | head -n 1)

# Convert with deduplication
python3 -c "
import sys, re
seen = set()
with open('$VTT_FILE', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('WEBVTT') and not line.startswith('Kind:') and not line.startswith('Language:') and '-->' not in line:
            clean = re.sub('<[^>]*>', '', line)
            clean = clean.replace('&amp;', '&').replace('&gt;', '>').replace('&lt;', '<')
            if clean and clean not in seen:
                print(clean)
                seen.add(clean)
" > "${VIDEO_TITLE}.txt"

echo "✓ Saved to: ${VIDEO_TITLE}.txt"

# Clean up VTT file
rm "$VTT_FILE"
echo "✓ Cleaned up temporary VTT file"
```

## Output Formats

- **VTT format** (`.vtt`): Includes timestamps and formatting, good for video players
- **Plain text** (`.txt`): Just the text content, good for reading or analysis

## Tips

- The filename will be `{output_name}.{language_code}.vtt` (e.g., `transcript.en.vtt`)
- Most YouTube videos have auto-generated English subtitles
- Some videos may have multiple language options
- If auto-subtitles aren't available, try `--write-sub` instead for manual subtitles

## Complete Workflow Example

```bash
VIDEO_URL="https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Get video title for filename
VIDEO_TITLE=$(yt-dlp --print "%(title)s" "$VIDEO_URL" | tr '/' '_' | tr ':' '-' | tr '?' '' | tr '"' '')
OUTPUT_NAME="transcript_temp"

# ============================================
# STEP 1: Check if yt-dlp is installed
# ============================================
if ! command -v yt-dlp &> /dev/null; then
    echo "yt-dlp is required but not installed; install it in a user-managed environment and retry." >&2
    exit 1
fi

# ============================================
# STEP 2: List available subtitles
# ============================================
echo "Checking available subtitles..."
yt-dlp --list-subs "$VIDEO_URL"

# ============================================
# STEP 3: Try manual subtitles first
# ============================================
echo "Attempting to download manual subtitles..."
if yt-dlp --write-sub --skip-download --output "$OUTPUT_NAME" "$VIDEO_URL" 2>/dev/null; then
    echo "✓ Manual subtitles downloaded successfully!"
    ls -lh ${OUTPUT_NAME}.*
else
    # ============================================
    # STEP 4: Fallback to auto-generated
    # ============================================
    echo "Manual subtitles not available. Trying auto-generated..."
    if yt-dlp --write-auto-sub --skip-download --output "$OUTPUT_NAME" "$VIDEO_URL" 2>/dev/null; then
        echo "✓ Auto-generated subtitles downloaded successfully!"
        ls -lh ${OUTPUT_NAME}.*
    else
        # ============================================
        # STEP 5: Last resort - Whisper transcription
        # ============================================
        echo "⚠ No subtitles available for this video."

        # Get file size
        FILE_SIZE=$(yt-dlp --print "%(filesize_approx)s" -f "bestaudio" "$VIDEO_URL")
        DURATION=$(yt-dlp --print "%(duration)s" "$VIDEO_URL")
        TITLE=$(yt-dlp --print "%(title)s" "$VIDEO_URL")

        echo "Video: $TITLE"
        echo "Duration: $((DURATION / 60)) minutes"
        echo "Audio size: ~$((FILE_SIZE / 1024 / 1024)) MB"
        echo ""
        echo "Would you like to download and transcribe with Whisper? (y/n)"
        read -r RESPONSE

        if [[ "$RESPONSE" =~ ^[Yy]$ ]]; then
            # Check for Whisper
            if ! command -v whisper &> /dev/null; then
                echo "Whisper is an optional prerequisite and is not installed." >&2
                echo "Install openai-whisper in a user-managed isolated environment, then rerun." >&2
                exit 1
            fi

            # Download audio
            echo "Downloading audio..."
            yt-dlp -x --audio-format mp3 --output "audio_%(id)s.%(ext)s" "$VIDEO_URL"

            # Get the actual audio filename
            AUDIO_FILE=$(ls audio_*.mp3 | head -n 1)

            # Transcribe
            echo "Transcribing with Whisper (this may take a few minutes)..."
            whisper "$AUDIO_FILE" --model base --output_format vtt

            # Cleanup
            echo "Transcription complete! Delete audio file? (y/n)"
            read -r CLEANUP_RESPONSE
            if [[ "$CLEANUP_RESPONSE" =~ ^[Yy]$ ]]; then
                rm "$AUDIO_FILE"
                echo "Audio file deleted."
            fi

            ls -lh *.vtt
        else
            echo "Transcription cancelled."
            exit 0
        fi
    fi
fi

# ============================================
# STEP 6: Convert to readable plain text with deduplication
# ============================================
VTT_FILE=$(ls ${OUTPUT_NAME}*.vtt 2>/dev/null || ls *.vtt | head -n 1)
if [ -f "$VTT_FILE" ]; then
    echo "Converting to readable format and removing duplicates..."
    python3 -c "
import sys, re
seen = set()
with open('$VTT_FILE', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('WEBVTT') and not line.startswith('Kind:') and not line.startswith('Language:') and '-->' not in line:
            clean = re.sub('<[^>]*>', '', line)
            clean = clean.replace('&amp;', '&').replace('&gt;', '>').replace('&lt;', '<')
            if clean and clean not in seen:
                print(clean)
                seen.add(clean)
" > "${VIDEO_TITLE}.txt"
    echo "✓ Saved to: ${VIDEO_TITLE}.txt"

    # Clean up temporary VTT file
    rm "$VTT_FILE"
    echo "✓ Cleaned up temporary VTT file"
else
    echo "⚠ No VTT file found to convert"
fi

echo "✓ Complete!"
```

**Note**: This complete workflow requires the catalog's `yt-dlp` prerequisite
to be installed before it starts.

## Error Handling

### Common Issues and Solutions:

**1. yt-dlp not installed**
- Report the missing declared prerequisite and provide a manual installation link
- Verify installation before proceeding

**2. No subtitles available**
- List available subtitles first to confirm
- Try both `--write-sub` and `--write-auto-sub`
- If both fail, offer Whisper transcription option
- Show file size and ask for user confirmation before downloading audio

**3. Invalid or private video**
- Check if URL is correct format: `https://www.youtube.com/watch?v=VIDEO_ID`
- Some videos may be private, age-restricted, or geo-blocked
- Inform user of the specific error from yt-dlp

**4. Whisper installation fails**
- May require system dependencies (ffmpeg, rust)
- Require installation in a user-managed isolated environment; do not mutate ambient Python
- Check available disk space (models require 1-10GB depending on size)

**5. Download interrupted or failed**
- Check internet connection
- Verify sufficient disk space
- Try again with `--no-check-certificate` if SSL issues occur

**6. Multiple subtitle languages**
- By default, yt-dlp downloads all available languages
- Can specify with `--sub-langs en` for English only
- List available with `--list-subs` first

### Best Practices:

- ✅ Always check what's available before attempting download (`--list-subs`)
- ✅ Verify success at each step before proceeding to next
- ✅ Ask user before large downloads (audio files, Whisper models)
- ✅ Clean up temporary files after processing
- ✅ Provide clear feedback about what's happening at each stage
- ✅ Handle errors gracefully with helpful messages
