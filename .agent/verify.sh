#!/bin/sh
# Offline checks for this repo, run by the verify-turn hook after approval.
set -e
cd "$(dirname "$0")/.."
exec hooks/test/run.sh
