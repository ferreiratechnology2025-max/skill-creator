#!/bin/bash
# test.sh - Test suite for landing-page-generator (Linux/Mac)
# Usage: chmod +x test.sh && ./test.sh

set -e

SCRIPTS_DIR="scripts"
OUTPUT_DIR="output/test-suite"
EVALS_DIR="evals/inputs"

FALHAS=0

echo "========================================"
echo "Landing Page Generator - Test Suite"
echo "========================================"
echo ""

# Clean previous output
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

echo "[1/4] Testing landing-page template..."
echo "-----------------------------------------------"
# --test-all separa a saida por template (output/test-suite/<template>/<slug>)
python "$SCRIPTS_DIR/generate.py" --test-all --output "$OUTPUT_DIR" || true
echo ""

echo "[2/4] Testing proposta-comercial template..."
echo "-----------------------------------------------"
python "$SCRIPTS_DIR/generate.py" --template proposta "$EVALS_DIR/proposta_teste.json" --output "$OUTPUT_DIR/proposta" || {
    echo "[ERROR] Failed to generate proposal."
    FALHAS=$((FALHAS + 1))
}
echo "[OK] Proposal generated."
echo ""

echo "[3/4] Running QA on generated landing pages..."
echo "-----------------------------------------------"
# check.py valida convencoes do template landing-page (CTA, LGPD) --
# roda so sobre output/test-suite/landing-page, nao sobre output/test-suite/proposta,
# que e' outro contrato (documento de orcamento, sem CTA nem rodape LGPD por design).
for dir in "$OUTPUT_DIR/landing-page"/*/; do
    if [ -f "${dir}index.html" ]; then
        name=$(basename "$dir")
        echo "Checking: $name"
        python "$SCRIPTS_DIR/check.py" "${dir}index.html" || FALHAS=$((FALHAS + 1))
        echo ""
    fi
done

echo "[4/4] Regression: schema drives validation (Fase 5, gate 2)..."
echo "-----------------------------------------------"
python "$SCRIPTS_DIR/test_schema_reflete.py" || FALHAS=$((FALHAS + 1))
echo ""

echo "========================================"
if [ "$FALHAS" -eq 0 ]; then
    echo "Tests completed! All 4 stages passed."
    echo "========================================"
    exit 0
else
    echo "Tests completed with $FALHAS stage(s) failing."
    echo "========================================"
    exit 1
fi
