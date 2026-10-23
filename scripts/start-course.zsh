#!/bin/zsh
# Credentials stay in this process; no key is saved to disk.
set -eu
cd "${0:A:h:h}"
if [[ ! -x .venv/bin/python ]]; then
  print 'Create .venv and install requirements.txt first. See README.md.'
  exit 1
fi
if [[ -z "${COURSE_API_KEY:-}" ]]; then
  read -rs 'COURSE_API_KEY?Paste course API key (hidden), then Enter: '
  print
fi
if [[ -z "$COURSE_API_KEY" ]]; then
  print 'Course API key is required.'
  exit 1
fi
COURSE_MODEL=${COURSE_MODEL:-qwen3.8-flash}
export COURSE_API_KEY COURSE_MODEL
if [[ "${1:-}" == "--check" ]]; then
  exec .venv/bin/python scripts/check_course.py
fi
exec .venv/bin/python app.py "$@"
