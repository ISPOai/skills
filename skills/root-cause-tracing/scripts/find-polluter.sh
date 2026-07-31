#!/usr/bin/env bash
# Find which test first creates an unwanted file or directory.
# Usage: find-polluter.sh <path-to-check> <find-path-pattern> [test-command...]
# Example: find-polluter.sh '.git' '*/src/*.test.ts' npm test --

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <path-to-check> <find-path-pattern> [test-command...]" >&2
  exit 2
fi

pollution_check=$1
test_pattern=$2
shift 2

if [[ -e "$pollution_check" ]]; then
  echo "Refusing to start: $pollution_check already exists." >&2
  echo "Move or remove it deliberately before running the diagnostic." >&2
  exit 2
fi

if [[ $# -gt 0 ]]; then
  test_command=("$@")
else
  test_command=(npm test --)
fi

test_files=()
while IFS= read -r -d '' test_file; do
  test_files+=("$test_file")
done < <(find . -type f -path "$test_pattern" -print0 | sort -z)

total=${#test_files[@]}
if [[ $total -eq 0 ]]; then
  echo "No test files matched find path pattern: $test_pattern" >&2
  exit 2
fi

echo "Searching $total tests for the first one that creates: $pollution_check"

count=0
for test_file in "${test_files[@]}"; do
  count=$((count + 1))
  echo "[$count/$total] $test_file"
  "${test_command[@]}" "$test_file" >/dev/null 2>&1 || true

  if [[ -e "$pollution_check" ]]; then
    echo "Polluter found: $test_file"
    echo "Created: $pollution_check"
    ls -la "$pollution_check"
    exit 1
  fi
done

echo "No polluter found; all matched tests left the target absent."
