#!/usr/bin/env python3
"""
check.py v2 - QA de proveniencia para paginas de site institucional.

Uso:
    python scripts/check.py output/<pagina>.html

Roda verificacoes objetivas, incluindo a regra central da skill: todo claim
de aparencia factual precisa de um marcador de proveniencia (comentario
PLACEHOLDER ou "fonte:") nas linhas imediatamente acima. Categorias
cobertas: CRO/CNPJ, preco, telefone, contagem de clientes/anos (v1) + ano
de fundacao, prazo em dias uteis, parcelamento, promessa de "mesmo dia" e
duracao de consultas (v2, hotfix 1.3.0). Falso positivo ocasional e
aceitavel -- o check existe para forcar a pergunta certa, nao para ser
perfeito, e so cobre as categorias listadas -- uma categoria nova de claim
factual sem regex correspondente passa despercebida ate ser adicionada.

Sai com codigo 1 se qualquer verificacao falhar.
"""
import re
import sys
from pathlib import Path

JANELA_LINHAS = 20

PADROES_CREDENCIAL = [
    r"(?i)(api[_-]?key|secret|token|senha|password)\s*[:=]\s*['\"][^'\"]{8,}",
    r"sk-[a-zA-Z0-9]{20,}",
    r"AKIA[0-9A-Z]{16}",
]

PADROES_CLAIM_FACTUAL = [
    ("CRO/CNPJ", r"(?i)CRO-?[A-Z]{0,2}\s*\d{3,}|\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}"),
    ("Preco (R$)", r"R\$\s*[\d.,]+"),
    ("Telefone", r"\(\d{2}\)\s*\d{4,5}-?\d{4}"),
    ("Contagem (clientes/pacientes/anos)",
     r"(?i)\d[\d.,]*\+?\s*(pacientes|clientes|anos de|avalia\w*|atendimentos)"),
    # v2: promessas operacionais (adicionado no hotfix 1.3.0)
    ("Ano de fundacao", r"(?i)desde\s+\d{4}"),
    # nota: "util" (singular) e "uteis" (plural) nao sao flexao regular por
    # "s" -- alternancia explicita em vez de "uteis?", que nao bateria "util"
    ("Prazo em dias uteis", r"(?i)\d+\s+dias?\s+(út|ut)(il|eis)"),
    ("Parcelamento", r"(?i)\d+x\s*(sem juros|no cart[aã]o)"),
    ("Promessa temporal (mesmo dia)", r"(?i)mesmo dia"),
    ("Duracao (minutos/horas)", r"(?i)\d+\s*(min|minutos?|horas?)\b"),
]

MARCADOR_PROVENIENCIA = re.compile(r"(?i)PLACEHOLDER|fonte\s*:\s*(usu[aá]rio|busca|placeholder)")


def checar(caminho):
    html = caminho.read_text(encoding="utf-8")
    linhas = html.splitlines()
    resultados = []

    def check(nome, ok, detalhe=""):
        resultados.append((nome, ok, detalhe))

    check("Zero credenciais expostas",
          not any(re.search(p, html) for p in PADROES_CREDENCIAL))

    titulo = re.search(r"<title>(.*?)</title>", html, re.DOTALL)
    check("Tag <title> presente e <= 90 caracteres",
          bool(titulo) and len(titulo.group(1).strip()) <= 90,
          "{} chars".format(len(titulo.group(1).strip())) if titulo else "ausente")

    meta = re.search(r'<meta name="description" content="([^"]*)"', html)
    check("Meta description presente e <= 160 caracteres",
          bool(meta) and 0 < len(meta.group(1)) <= 160,
          "{} chars".format(len(meta.group(1))) if meta else "ausente")

    check("Viewport mobile configurado", 'name="viewport"' in html)

    # Regra central: todo claim de aparencia factual tem proveniencia
    # declarada nas JANELA_LINHAS linhas anteriores.
    sem_proveniencia = []
    ultimo_marcador = -10**9
    for i, linha in enumerate(linhas):
        if MARCADOR_PROVENIENCIA.search(linha):
            ultimo_marcador = i
        for nome_padrao, padrao in PADROES_CLAIM_FACTUAL:
            for m in re.finditer(padrao, linha):
                if i - ultimo_marcador > JANELA_LINHAS:
                    sem_proveniencia.append(
                        "linha {}: {} ({!r})".format(i + 1, nome_padrao, m.group(0)))

    check("Claims de aparencia factual com proveniencia declarada",
          not sem_proveniencia,
          "; ".join(sem_proveniencia[:8]) + (" ..." if len(sem_proveniencia) > 8 else ""))

    falhas = 0
    total = len(resultados)
    for nome, ok, detalhe in resultados:
        simbolo = "[OK]" if ok else "[FAIL]"
        extra = " -- {}".format(detalhe) if detalhe and not ok else ""
        print("{} {}{}".format(simbolo, nome, extra))
        falhas += 0 if ok else 1

    print("\n{}/{} checks passaram".format(total - falhas, total))
    return 1 if falhas else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(checar(Path(sys.argv[1])))
