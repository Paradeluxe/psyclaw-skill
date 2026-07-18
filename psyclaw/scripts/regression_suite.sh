#!/usr/bin/env bash
# regression_suite.sh — end-to-end smoke test for all psyclaw example specs.
#
# Runs:
#   1. harness_cli.py on every examples/*.yaml
#   2. validate_load_from_xml.py on every produced .psyexp
#
# Exits 0 iff all .psyexp files load clean (zero warnings).
#
# Run with PsychoPy's python (D:\\Software\\P\\python.exe), NOT hermes python.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
EXAMPLES_DIR="$SKILL_DIR/examples"
OUT_DIR="$SKILL_DIR/.regression_out"

PY="D:/Software/P/python.exe"
[ -x "$PY" ] || { echo "PsychoPy python not at $PY"; exit 2; }

mkdir -p "$OUT_DIR"

# Strip hermes-agent path pollution
export PYTHONPATH=
export PYTHONHOME=
export PYTHONNOUSERSITE=1

PASS=0
FAIL=0

for spec in "$EXAMPLES_DIR"/*.yaml "$EXAMPLES_DIR"/*/*.yaml; do
    [ -f "$spec" ] || continue
    name=$(basename "$spec" .yaml)
    parent=$(basename "$(dirname "$spec")")
    tag="${parent}__${name}"
    outdir="$OUT_DIR/$tag"
    rm -rf "$outdir"
    mkdir -p "$outdir"

    echo "=== $tag ==="
    if ! "$PY" "$SCRIPT_DIR/harness_cli.py" --spec "$spec" --out-dir "$outdir" 2>&1 | tail -3; then
        echo "  [FAIL] harness_cli"
        FAIL=$((FAIL+1))
        continue
    fi

    psyexp=$(find "$outdir" -name "*.psyexp" -type f 2>/dev/null | head -1)
    if [ -z "$psyexp" ]; then
        echo "  [FAIL] no .psyexp produced"
        FAIL=$((FAIL+1))
        continue
    fi

    if "$PY" "$SCRIPT_DIR/validate_load_from_xml.py" "$psyexp" 2>&1 | tail -1; then
        PASS=$((PASS+1))
    else
        FAIL=$((FAIL+1))
    fi
done

echo
echo "===== regression: $PASS passed, $FAIL failed ====="
[ "$FAIL" -eq 0 ]
