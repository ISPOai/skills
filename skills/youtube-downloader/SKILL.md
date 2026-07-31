---
name: youtube-downloader
description: Download YouTube videos with customizable quality and format options. Use this skill when the user asks to download, save, or grab YouTube videos. Supports various quality settings (best, 1080p, 720p, 480p, 360p), multiple formats (mp4, webm, mkv), and audio-only downloads as MP3.
---

# YouTube Video Downloader

Download YouTube videos with full control over quality and format settings.

Before invoking the helper, resolve `youtube_downloader_dir` to the directory
containing this `SKILL.md`. `yt-dlp` is a declared prerequisite: if it is not
available, report that requirement instead of modifying the user's Python or
system package environment.

## Quick Start

The simplest way to download a video:

```bash
python "$youtube_downloader_dir/scripts/download_video.py" "https://www.youtube.com/watch?v=VIDEO_ID"
```

This downloads the video in best available quality as MP4 to
`./outputs/youtube/` in the active workspace.

## Options

### Quality Settings

Use `-q` or `--quality` to specify video quality:

- `best` (default): Highest quality available
- `1080p`: Full HD
- `720p`: HD
- `480p`: Standard definition
- `360p`: Lower quality
- `worst`: Lowest quality available

Example:
```bash
python "$youtube_downloader_dir/scripts/download_video.py" "URL" -q 720p
```

### Format Options

Use `-f` or `--format` to specify output format (video downloads only):

- `mp4` (default): Most compatible
- `webm`: Modern format
- `mkv`: Matroska container

Example:
```bash
python "$youtube_downloader_dir/scripts/download_video.py" "URL" -f webm
```

### Audio Only

Use `-a` or `--audio-only` to download only audio as MP3:

```bash
python "$youtube_downloader_dir/scripts/download_video.py" "URL" -a
```

### Custom Output Directory

Use `-o` or `--output` to specify a different output directory:

```bash
python "$youtube_downloader_dir/scripts/download_video.py" "URL" -o /path/to/directory
```

## Complete Examples

1. Download video in 1080p as MP4:
```bash
python "$youtube_downloader_dir/scripts/download_video.py" "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -q 1080p
```

2. Download audio only as MP3:
```bash
python "$youtube_downloader_dir/scripts/download_video.py" "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -a
```

3. Download in 720p as WebM to custom directory:
```bash
python "$youtube_downloader_dir/scripts/download_video.py" "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -q 720p -f webm -o /custom/path
```

## How It Works

The skill uses `yt-dlp`, a robust YouTube downloader that:
- Requires the declared `yt-dlp` command; the helper does not install packages
- Fetches video information before downloading
- Selects the best available streams matching your criteria
- Merges video and audio streams when needed
- Supports a wide range of YouTube video formats

## Important Notes

- Downloads are saved to `./outputs/youtube/` by default
- Video filename is automatically generated from the video title
- A missing `yt-dlp` prerequisite produces an actionable error without changing
  the ambient package environment
- Only single videos are downloaded (playlists are skipped by default)
- Higher quality videos may take longer to download and use more disk space
