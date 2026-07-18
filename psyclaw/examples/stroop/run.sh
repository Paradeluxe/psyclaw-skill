#!/bin/bash
set -e
cd "$( dirname "${BASH_SOURCE[0]}" )"
if command -v psychopy &> /dev/null; then
    psychopy "stroop_experiment.psyexp"
else
    echo "PsychoPy not found. Install from https://www.psychopy.org/"
fi
