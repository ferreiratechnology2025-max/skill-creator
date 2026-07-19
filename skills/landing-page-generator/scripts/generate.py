#!/usr/bin/env python3
"""
generate.py - Motor de renderizacao de landing pages a partir de template parametrizado.

Uso basico:
    python scripts/generate.py params.json

Uso avancado (template especifico):
    python scripts/generate.py --template proposta params.json

Uso com saida especifica:
    python scripts/generate.py params.json --output output/

Uso com modo batch (todos os testes):
    python scripts/generate.py --test-all

Deterministico, stdlib apenas. Falha rapido com mensagens claras.
Suporta placeholders {{VAR}} e blocos de lista {{#LISTA}}...{{/LISTA}}.
"""
import json
import re
import sys
import unicodedata
import logging
import argparse
from datetime import date
from html import escape
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_DIR / "assets" / "templates"

DEFAULTS = {
    "CHAMADA_FINAL": "Pronto para comecar?",
    "COR_PRIMARIA": "#2563eb",
    "COR_ESCURA": "#1e3a8a",
}

# Obrigatorias por template
OBRIGATORIAS_LANDING = ["NOME_NEGOCIO", "TITULO_HERO", "SUBTITULO", "CTA_TEXTO", "LINK_CTA", "CIDADE", "BENEFICIOS"]
OBRIGATORIAS_PROPOSTA = ["CLIENTE", "PROJETO", "VALOR", "SERVICOS", "PRAZO"]
LIMITES = {"TITULO_HERO": 80, "SUBTITULO": 200, "CTA_TEXTO": 30, "META_DESCRICAO": 160}
COR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
URL_RE = re.compile(r"^https?://")

# Casos que devem falhar (edge cases de validacao, nao cross-template)
EXPECTED_FAILS = {
    "edge_title_curto.json",
    "edge_title_longo.json",
    "edge_beneficios_1.json",
    "edge_beneficios_7.json",
    "real_lead_3_consultoria.json",
    "tc_004.json",
}


def resolve_template(params):
    """Resolve o template para um caso de teste.

    Usa o campo explicito 'template' do params se presente (spec-driven).
    Fallback heuristico para retrocompatibilidade quando o campo nao existir.
    """
    if "template" in params:
        return params.pop("template")
    if "CLIENTE" in params and "PROJETO" in params and "VALOR" in params:
        return "proposta"
    return "landing-page"


def slugify(texto):
    """Normaliza nome para slug URL-safe."""
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto).strip("-").lower()
    return texto or "landing-page"


def load_template(template_name):
    """Carrega template do disco (sem cache)."""
    template_path = TEMPLATES_DIR / template_name / "index.html"
    if not template_path.exists():
        raise FileNotFoundError("Template nao encontrado: {}".format(template_path))
    logger.debug("Template carregado: %s", template_name)
    return template_path.read_text(encoding="utf-8")


def load_schema(template_name):
    """Carrega schema/template.json (sem cache)."""
    schema_path = TEMPLATES_DIR / template_name / "template.json"
    if schema_path.exists():
        logger.debug("Schema carregado: %s", template_name)
        return json.loads(schema_path.read_text(encoding="utf-8"))
    return None


def validar(params, template_name="landing-page"):
    """Valida parametros com base nas regras do template."""
    erros = []
    avisos = []

    # Determinar obrigatorias com base no template
    obrigatorias = OBRIGATORIAS_PROPOSTA if template_name == "proposta" else OBRIGATORIAS_LANDING

    # Validacoes obrigatorias basicas
    for chave in obrigatorias:
        if not params.get(chave):
            erros.append("Variavel obrigatoria ausente ou vazia: {}".format(chave))

    # Validacoes de comprimento
    for chave, limite in LIMITES.items():
        valor = params.get(chave)
        if isinstance(valor, str) and len(valor) > limite:
            erros.append("{} excede {} caracteres ({}). Reduza.".format(chave, limite, len(valor)))

    # Minimo de caracteres para TITULO_HERO
    titulo = params.get("TITULO_HERO", "")
    if isinstance(titulo, str) and 0 < len(titulo) < 10:
        erros.append("TITULO_HERO deve ter pelo menos 10 caracteres (tem {})".format(len(titulo)))

    # Validar SUBTITULO minimo
    subt = params.get("SUBTITULO", "")
    if isinstance(subt, str) and 0 < len(subt) < 20:
        avisos.append("SUBTITULO com apenas {} caracteres (recomendado >= 20)".format(len(subt)))

    # Validar beneficios
    beneficios = params.get("BENEFICIOS")
    if isinstance(beneficios, list):
        if not (3 <= len(beneficios) <= 10):
            erros.append("BENEFICIOS deve ter entre 3 e 10 itens (tem {})".format(len(beneficios)))
        for i, item in enumerate(beneficios):
            if not isinstance(item, dict) or not item.get("titulo") or not item.get("descricao"):
                erros.append("BENEFICIOS[{}] precisa dos campos 'titulo' e 'descricao'".format(i))
            else:
                if len(str(item.get("titulo", ""))) > 60:
                    avisos.append("BENEFICIOS[{}] titulo excede 60 caracteres".format(i))
                if len(str(item.get("descricao", ""))) > 120:
                    avisos.append("BENEFICIOS[{}] descricao excede 120 caracteres".format(i))
    elif beneficios is not None:
        erros.append("BENEFICIOS deve ser uma lista de objetos {titulo, descricao}")

    # Auto-correcao de cores invalidas -> fallback
    for chave in ("COR_PRIMARIA", "COR_ESCURA"):
        if chave in params and not COR_RE.match(str(params[chave])):
            avisos.append("{} invalida '{}' -> fallback para {}".format(chave, params[chave], DEFAULTS[chave]))
            params[chave] = DEFAULTS[chave]

    # Auto-correcao de URL sem protocolo
    link = params.get("LINK_CTA", "")
    if link and not URL_RE.match(str(link)):
        link_str = str(link)
        if not link_str.startswith("http"):
            params["LINK_CTA"] = "https://" + link_str
            avisos.append("LINK_CTA sem protocolo -> corrigido para https://" + link_str)

    # Validar CTA_TEXTO minimo
    cta = params.get("CTA_TEXTO", "")
    if isinstance(cta, str) and len(cta) < 3:
        avisos.append("CTA_TEXTO muito curto ({} chars). Recomenda-se pelo menos 3.".format(len(cta)))

    return erros, avisos


def renderizar(template, params):
    """Renderiza template substituindo placeholders pelos valores."""
    # 1. Blocos de lista {{#NOME}}...{{/NOME}}
    def render_bloco(m):
        nome, corpo = m.group(1), m.group(2)
        itens = params.get(nome, [])
        partes = []
        for item in itens:
            if isinstance(item, dict):
                trecho = corpo
                for k, v in item.items():
                    trecho = trecho.replace("{{" + k + "}}", escape(str(v)))
                partes.append(trecho)
            elif isinstance(item, str):
                partes.append(corpo.replace("{{.}}", escape(item)))
        return "".join(partes)

    saida = re.sub(r"\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}", render_bloco, template, flags=re.DOTALL)

    # 2. Placeholders simples
    sem_escape = {"LINK_CTA", "COR_PRIMARIA", "COR_ESCURA"}
    for k, v in params.items():
        if isinstance(v, (str, int)):
            valor = str(v) if k in sem_escape else escape(str(v))
            saida = saida.replace("{{" + k + "}}", valor)

    # 3. Placeholders de lista simples {{.}} (para templates como proposta)
    if "SERVICOS" in params:
        servicos = params["SERVICOS"]
        if isinstance(servicos, list) and servicos and isinstance(servicos[0], str):
            partes = []
            for item in servicos:
                partes.append("<li>{}</li>".format(escape(str(item))))
            saida = saida.replace("{{.}}", "PLACEHOLDER_SERVICO_SENTINELA")
            saida = saida.replace("PLACEHOLDER_SERVICO_SENTINELA", "\n".join(partes))

    return saida


def gerar(params, template_name="landing-page", out_base=None):
    """Funcao principal de geracao. Retorna dict com status."""
    if out_base is None:
        out_base = SKILL_DIR / "output"

    # Validar
    erros, avisos = validar(params, template_name)

    if erros:
        logger.error("VALIDACAO FALHOU:")
        for e in erros:
            logger.error("  [!] %s", e)
        return {
            "status": "erro",
            "erros": erros,
            "avisos": avisos,
            "slug": None,
            "output_path": None,
        }

    # Carregar template
    try:
        template = load_template(template_name)
    except FileNotFoundError as e:
        logger.error(str(e))
        return {
            "status": "erro",
            "erros": [str(e)],
            "avisos": avisos,
            "slug": None,
            "output_path": None,
        }

    # Aplicar defaults
    for k, v in DEFAULTS.items():
        params.setdefault(k, v)
    params.setdefault("ANO", date.today().year)
    params.setdefault("META_DESCRICAO", params.get("SUBTITULO", ""))

    # Renderizar
    html = renderizar(template, params)

    # Verificar placeholders remanescentes
    restantes = sorted(set(re.findall(r"\{\{[#/]?\w+\}\}", html)))
    if restantes:
        logger.error("Placeholders nao preenchidos: %s", ", ".join(restantes))
        return {
            "status": "erro",
            "erros": ["Placeholders nao preenchidos: " + ", ".join(restantes)],
            "avisos": avisos,
            "slug": None,
            "output_path": None,
        }

    # Gerar slug e salvar
    if template_name == "proposta":
        slug_key = "CLIENTE"
    else:
        slug_key = "NOME_NEGOCIO"
    slug = params.get("SLUG") or slugify(params.get(slug_key, "documento"))
    destino = out_base / slug
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "index.html").write_text(html, encoding="utf-8")
    (destino / "params.json").write_text(
        json.dumps(params, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    logger.info("[OK] Gerado: %s", destino / "index.html")
    logger.info("[OK] Parametros arquivados: %s", destino / "params.json")
    if avisos:
        for a in avisos:
            logger.warning("[AVISO] %s", a)

    return {
        "status": "sucesso",
        "slug": slug,
        "output_path": str(destino / "index.html"),
        "params_path": str(destino / "params.json"),
        "erros": [],
        "avisos": avisos,
    }


def main():
    parser = argparse.ArgumentParser(description="Gerador de landing pages")
    parser.add_argument("params_file", nargs="?", help="Arquivo JSON com parametros")
    parser.add_argument("--template", default="landing-page", help="Nome do template (default: landing-page)")
    parser.add_argument("--output", default=None, help="Diretorio de saida")
    parser.add_argument("--test-all", action="store_true", help="Executar todos os testes em evals/inputs/")
    parser.add_argument("--quiet", action="store_true", help="Silenciar logs (apenas erros)")

    args = parser.parse_args()

    if args.quiet:
        logger.setLevel(logging.ERROR)

    # Modo batch: executar todos os testes
    if args.test_all:
        inputs_dir = SKILL_DIR / "evals" / "inputs"
        if not inputs_dir.exists():
            logger.error("Diretorio de testes nao encontrado: %s", inputs_dir)
            return 1

        out_base = Path(args.output) if args.output else SKILL_DIR / "output" / "test-suite"
        out_base.mkdir(parents=True, exist_ok=True)

        results = []
        for f in sorted(inputs_dir.glob("*.json")):
            try:
                params = json.loads(f.read_text(encoding="utf-8"))
                template = resolve_template(params)
                result = gerar(params, template, out_base)
                result["input_file"] = f.name
                result["template_usado"] = template
                results.append(result)
            except Exception as e:
                results.append({"input_file": f.name, "status": "erro", "erros": [str(e)], "avisos": []})

        # Resumo
        total = len(results)
        sucesso = sum(1 for r in results if r["status"] == "sucesso")
        blocked = sum(1 for r in results if r["status"] == "erro")
        expected_blocked = sum(1 for r in results if r["status"] == "erro" and r.get("input_file", "") in EXPECTED_FAILS)
        real_errors = blocked - expected_blocked

        print("\n" + "=" * 60)
        print("RESUMO DOS TESTES")
        print("=" * 60)
        for r in results:
            simbolo = "[OK]" if r["status"] == "sucesso" else "[BLOCKED]"
            if r["input_file"] in EXPECTED_FAILS:
                simbolo = "[EDGE]"
            template_info = r.get("template_usado", args.template)
            print("{} {} - {} (template: {})".format(simbolo, r["input_file"], r["status"], template_info))
            if r.get("avisos"):
                for a in r["avisos"]:
                    print("    [AVISO] {}".format(a))
        print("=" * 60)
        print("Total: {} | Sucesso: {} | Bloqueios (esperados): {} | Erros reais: {}".format(
            total, sucesso, expected_blocked, real_errors))
        print("=" * 60)

        return 0 if real_errors == 0 else 1

    # Modo normal: gerar a partir de um arquivo
    if not args.params_file:
        parser.print_help()
        return 2

    caminho_params = Path(args.params_file)
    out_base = Path(args.output) if args.output else (SKILL_DIR / "output")

    try:
        params = json.loads(caminho_params.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        logger.error("ERRO ao ler %s: %s", caminho_params, e)
        return 1

    result = gerar(params, args.template, out_base)

    if result["status"] == "erro":
        return 1

    # Imprimir resultado JSON para integracao com outras ferramentas
    print("\nRESULTADO JSON:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
