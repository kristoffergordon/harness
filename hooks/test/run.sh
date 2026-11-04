#!/usr/bin/env bash
# Run all offline hook tests.
set -e
cd "$(dirname "${BASH_SOURCE[0]}")"
python3 -I test_guard_bash.py
bash verify-turn-test.sh
