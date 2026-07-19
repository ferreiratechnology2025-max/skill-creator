#!/usr/bin/env python3
"""
check.py - QA independente da landing page gerada.

Uso:
    python scripts/check.py output/<slug>/index.html

Roda 8 verificacoes objetivas. Sai com codigo 1 se qualquer uma falhar.
"""
import re
import sys
from pathlib import Path

PADROES_CREDENCIAL = [
    r"(?i)(api[_-]?key|secret|token|senha|password)\s*[:=]\s*['\"][^'\"]{8,}",
    r"sk-[a-zA-Z0-9]{20,}",
    r"AKIA[0-9A-Z]{16}",
]


def checar(caminho):
    html = caminho.read_text(encoding="utf-8")
    resultados = []

    def check(nome, ok, detalhe=""):
        resultados.append((nome, ok, detalhe))

    check("Placeholders todos preenchidos",
          not re.search(r"\{\{[#/]?\w+\}\}", html),
          "restam placeholders {{...}}" if re.search(r"\{\{[#/]?\w+\}\}", html) else "")

    titulo = re.search(r"<title>(.*?)</title>", html, re.DOTALL)
    check("Tag <title> presente e <= 90 caracteres",
          bool(titulo) and len(titulo.group(1).strip()) <= 90,
          "{} chars".format(len(titulo.group(1).strip())) if titulo else "ausente")

    meta = re.search(r'<meta name="description" content="([^"]*)"', html)
    check("Meta description presente e <= 160 caracteres",
          bool(meta) and 0 < len(meta.group(1)) <= 160,
          "{} chars".format(len(meta.group(1))) if meta else "ausente")

    check("Viewport mobile configurado", 'name="viewport"' in html)

    ctas = re.findall(r'class="cta[^"]*"\s+(?:style="[^"]*"\s+)?href="([^"]+)"', html)
    check("Pelo menos 2 CTAs com link", len(ctas) >= 2, "{} encontrados".format(len(ctas)))

    check("Links de CTA sao absolutos (http/https)",
          all(u.startswith(("http://", "https://")) for u in ctas),
          "; ".join(u for u in ctas if not u.startswith("http")) or "")

    check("Mencao LGPD no rodape", "LGPD" in html)

    cred = any(re.search(p, html) for p in PADROES_CREDENCIAL)
    check("Zero credenciais expostas", not cred)

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
