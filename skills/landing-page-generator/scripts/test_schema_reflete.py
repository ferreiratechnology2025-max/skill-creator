#!/usr/bin/env python3
"""
test_schema_reflete.py - Teste de regressao permanente para a Fase 5.

Prova, por comportamento e nao por leitura de codigo, que generate.py
deriva validacao de template.json em vez de ter copia hardcoded (LIMITES/
OBRIGATORIAS_*, removidas na v1.2.0 do template). Este e o experimento
que reprovou o motor no gate da Fase 5 (TITULO_HERO 80->90 nao refletia),
promovido a teste automatizado -- regra sem check e intencao.

Uso:
    python scripts/test_schema_reflete.py

Sai com codigo 1 se o schema mudar e o comportamento nao acompanhar.
Restaura template.json ao estado original mesmo se o teste falhar.
"""
import sys
import json
import importlib.util
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = SKILL_DIR / "assets" / "templates" / "landing-page" / "template.json"

spec = importlib.util.spec_from_file_location("generate", SKILL_DIR / "scripts" / "generate.py")
generate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate)


def titulo_de_tamanho(n):
    base = "Seu sorriso novo com atendimento humanizado e cuidadoso garantido "
    while len(base) < n:
        base += "mais "
    return base[:n]


def params_teste(titulo):
    return {
        "NOME_NEGOCIO": "Teste Regressao Schema",
        "TITULO_HERO": titulo,
        "SUBTITULO": "Subtitulo de teste com mais de vinte caracteres para passar na validacao",
        "CTA_TEXTO": "Agendar avaliacao",
        "LINK_CTA": "https://wa.me/5511999999999?text=teste",
        "CIDADE": "Teste",
        "BENEFICIOS": [
            {"titulo": "Beneficio 1", "descricao": "Descricao do beneficio 1 para o teste de regressao"},
            {"titulo": "Beneficio 2", "descricao": "Descricao do beneficio 2 para o teste de regressao"},
            {"titulo": "Beneficio 3", "descricao": "Descricao do beneficio 3 para o teste de regressao"},
        ],
    }


def main():
    original = SCHEMA_PATH.read_text(encoding="utf-8")
    schema = json.loads(original)
    max_original = schema["variaveis"]["TITULO_HERO"]["max_comprimento"]
    max_novo = max_original + 10
    titulo_87pct = titulo_de_tamanho(max_original + 3)  # excede o limite original, cabe no novo

    try:
        # 1. Baseline: titulo excede o limite ORIGINAL -> deve bloquear
        erros_antes, _ = generate.validar(dict(params_teste(titulo_87pct)), schema)
        if not erros_antes:
            print("[FAIL] Baseline nao bloqueou um titulo que ja excedia o limite original.")
            print("       O teste em si esta errado, ou o motor nunca validou isto.")
            return 1
        print("[OK] Baseline: titulo de {} chars bloqueado com limite {} (esperado)".format(
            len(titulo_87pct), max_original))

        # 2. Muda o schema em disco (o unico jeito de simular "usuario editou template.json")
        schema["variaveis"]["TITULO_HERO"]["max_comprimento"] = max_novo
        SCHEMA_PATH.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")

        # 3. Recarrega o schema do disco -- exatamente o que gerar() faz via load_schema()
        schema_recarregado = generate.load_schema("landing-page")
        erros_depois, _ = generate.validar(dict(params_teste(titulo_87pct)), schema_recarregado)

        if erros_depois:
            print("[FAIL] Schema mudou de {} para {} mas o motor ainda bloqueia:".format(
                max_original, max_novo))
            for e in erros_depois:
                print("       {}".format(e))
            print("[FAIL] Ha uma copia hardcoded do limite em algum lugar do codigo.")
            print("       grep -n 'max_comprimento\\|TITULO_HERO' scripts/generate.py")
            return 1

        print("[OK] Apos schema {} -> {}, mesmo titulo de {} chars agora passa (sem tocar em .py)".format(
            max_original, max_novo, len(titulo_87pct)))
        print("\n[PASS] O motor deriva validacao do schema -- Fase 5, criterio 2, aprovado por construcao.")
        return 0

    finally:
        # Restaura o schema original sempre, falhe ou passe o teste.
        SCHEMA_PATH.write_text(original, encoding="utf-8")
        atual = SCHEMA_PATH.read_text(encoding="utf-8")
        if atual != original:
            print("[FAIL CRITICO] template.json nao foi restaurado corretamente.")
            sys.exit(2)


if __name__ == "__main__":
    sys.exit(main())
