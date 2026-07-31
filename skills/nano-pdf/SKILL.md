---
name: nano-pdf
description: "Edit text in existing PDFs via natural-language prompts."
---

# nano-pdf

Edit PDFs using natural-language instructions. Point it at a page and describe what to change. For structural PDF work (merge, split, forms, watermarks, creation), see the `pdf` skill; for text extraction from scans, see `ocr-and-documents`.

## Prerequisites

```bash
# Install as an isolated CLI with uv when available
uv tool install nano-pdf

# Or with pipx
pipx install nano-pdf
```

## Usage

```bash
nano-pdf edit <file.pdf> <page_number> "<instruction>"
```

## Examples

```bash
# Change a title on page 1
nano-pdf edit deck.pdf 1 "Change the title to 'Q3 Results' and fix the typo in the subtitle"

# Update a date on a specific page
nano-pdf edit report.pdf 3 "Update the date from January to February 2026"

# Fix content
nano-pdf edit contract.pdf 2 "Change the client name from 'Acme Corp' to 'Acme Industries'"
```

## Notes

- Never experiment on the only copy. Preserve the original and edit a named
  working copy or explicit output path supported by the installed version.
- Page indexing may vary by version. Check `nano-pdf --help` and verify the
  intended page before editing; do not "retry ±1" after altering the wrong page.
- Always render or open the output PDF and verify both the intended edit and
  surrounding layout; a file-size check is not sufficient.
- The tool uses an LLM under the hood — requires an API key (check `nano-pdf --help` for config)
- Works well for text changes; complex layout modifications may need a different approach
