---
name: youtube-content
description: Fetch YouTube transcripts and transform them into summaries, chapters, threads, blog posts, or timestamped quotes. Use when a user shares a YouTube URL or video id, asks what a video says, requests captions or a transcript, or wants video content repurposed into written formats.
---

# YouTube Content Tool

## Helper Script

Resolve `youtube_content_dir` to the directory containing this `SKILL.md`. Keep
the transient `uv` environment and download cache in a writable task scratch
directory; do not change `HOME` or install into an ambient Python environment.
Create the scratch directory once per task:

```bash
youtube_content_scratch="$(mktemp -d "${TMPDIR:-/tmp}/ispo-youtube-content.XXXXXX")"
mkdir -p "$youtube_content_scratch/uv-cache"
```

Invoke the helper through the same atomic dependency path every time. The
script accepts standard YouTube URLs, short links, Shorts, embeds, live links,
or a raw 11-character video id.

```bash
# JSON output
UV_CACHE_DIR="$youtube_content_scratch/uv-cache" uv run --no-project --with youtube-transcript-api python "$youtube_content_dir/scripts/fetch_transcript.py" "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
UV_CACHE_DIR="$youtube_content_scratch/uv-cache" uv run --no-project --with youtube-transcript-api python "$youtube_content_dir/scripts/fetch_transcript.py" "URL" --text-only

# With timestamps
UV_CACHE_DIR="$youtube_content_scratch/uv-cache" uv run --no-project --with youtube-transcript-api python "$youtube_content_dir/scripts/fetch_transcript.py" "URL" --timestamps

# Specific language with fallback chain
UV_CACHE_DIR="$youtube_content_scratch/uv-cache" uv run --no-project --with youtube-transcript-api python "$youtube_content_dir/scripts/fetch_transcript.py" "URL" --language tr,en
```

## Output Formats

After fetching the transcript, format it based on the user's request. Read
[`references/output-formats.md`](references/output-formats.md) when examples
would help.

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps

## Workflow

1. **Fetch** the transcript using the atomic helper command with `--text-only --timestamps`.
2. **Validate**: confirm the output is non-empty and in the expected language. If empty, retry without `--language` to get any available transcript.
3. **Chunk if needed**: if the transcript exceeds ~50K characters, split into overlapping chunks (~40K with 2K overlap) and summarize each chunk before merging.
4. **Transform** into the requested output format. If the user did not specify a format, default to a summary.
5. **Verify**: re-read the transformed output to check for coherence, correct timestamps, and completeness before presenting.

## No-transcript fallback

If every language attempt reports disabled or unavailable transcripts:

1. Use a transcript or caption file supplied by the user.
2. If the current project already has approved video-download and
   speech-to-text capabilities, offer to transcribe the audio with those tools;
   do not install new downloaders or transcription models implicitly.
3. Otherwise report that transcript-backed transformation is unavailable and
   ask for captions or a local media file. Do not invent a transcript or present
   a title/description-only summary as if it covered the video.

For private, age-restricted, or unavailable videos, relay the bounded error and
ask the user to verify access. If `uv` is unavailable, report the declared
prerequisite instead of mutating an ambient Python installation.
