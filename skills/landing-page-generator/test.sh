#!/bin/bash
# test.sh - Test suite for landing-page-generator (Linux/Mac)
# Usage: chmod +x test.sh && ./test.sh

set -e

SCRIPTS_DIR="scripts"
OUTPUT_DIR="output/test-suite"
EVALS_DIR="evals/inputs"

echo "========================================"
echo "Landing Page Generator - Test Suite"
echo "========================================"
echo ""

# Clean previous output
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

echo "[1/3] Testing landing-page template..."
echo "-----------------------------------------------"
python "$SCRIPTS_DIR/generate.py" --test-all --output "$OUTPUT_DIR" || true
echo ""

echo "[2/3] Testing proposta-comercial template..."
echo "-----------------------------------------------"
python "$SCRIPTS_DIR/generate.py" --template proposta "$EVALS_DIR/proposta_teste.json" --output "$OUTPUT_DIR" || {
    echo "[ERROR] Failed to generate proposal."
    exit 1
}
echo "[OK] Proposal generated successfully."
echo ""

echo "[3/3] Running QA on generated files..."
echo "-----------------------------------------------"
for dir in "$OUTPUT_DIR"/*/; do
    if [ -f "${dir}index.html" ]; then
        name=$(basename "$dir")
        echo "Checking: $name"
        python "$SCRIPTS_DIR/check.py" "${dir}index.html"
        echo ""
    fi
done

echo "========================================"
echo "Tests completed!"
echo "========================================"
