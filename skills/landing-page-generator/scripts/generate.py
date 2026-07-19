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

# Nenhuma regra de negocio (obrigatoriedade, limite, tipo, default) vive
# aqui como constante. Tudo isso e derivado de template.json em runtime --
# ver validar() e gerar(). O que resta hardcoded e so o que o JSON nao
# consegue expressar de forma estatica:
DEFAULT_SLUG_CAMPO = "NOME_NEGOCIO"
# "padrao" destes campos no schema e uma descricao em prosa de um valor
# dinamico ("(ano atual)", "(derivado de SUBTITULO)"), nao um literal --
# por isso ficam como computo explicito em vez de setdefault(schema.padrao).
DEFAULTS_DINAMICOS = {"ANO", "META_DESCRICAO"}

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


def validar(params, schema):
    """Valida parametros com base nas regras declaradas em schema['variaveis'].

    Toda obrigatoriedade, limite de comprimento, contagem de itens, padrao
    de regex e fallback de cor/url vem do schema -- se o schema nao declara
    a regra, ela nao e aplicada. Isso substitui as constantes OBRIGATORIAS_*
    e LIMITES que existiam ate a v1.4.x: eram copias hardcoded do que
    template.json ja dizia, e podiam (e ficaram) divergentes dele.
    """
    erros = []
    avisos = []
    variaveis = schema.get("variaveis", {})

    for chave, spec in variaveis.items():
        tipo = spec.get("tipo")
        obrigatorio = spec.get("obrigatorio", False)
        valor = params.get(chave)

        if obrigatorio and not valor:
            erros.append("Variavel obrigatoria ausente ou vazia: {}".format(chave))
            continue
        if valor is None:
            continue

        if isinstance(valor, str):
            min_c = spec.get("min_comprimento")
            max_c = spec.get("max_comprimento")
            if min_c is not None and 0 < len(valor) < min_c:
                erros.append("{} deve ter pelo menos {} caracteres (tem {})".format(chave, min_c, len(valor)))
            if max_c is not None and len(valor) > max_c:
                erros.append("{} excede {} caracteres ({}). Reduza.".format(chave, max_c, len(valor)))
            # "pattern" em tipo "cor" tem fallback silencioso (ver abaixo);
            # em qualquer outro tipo string, e um formato obrigatorio.
            pattern = spec.get("pattern")
            if pattern and tipo != "cor" and not re.match(pattern, valor):
                erros.append("{} nao corresponde ao formato esperado ({})".format(chave, pattern))

        if tipo == "lista":
            if not isinstance(valor, list):
                erros.append("{} deve ser uma lista".format(chave))
            else:
                min_i, max_i = spec.get("min_itens"), spec.get("max_itens")
                if min_i is not None and max_i is not None and not (min_i <= len(valor) <= max_i):
                    erros.append("{} deve ter entre {} e {} itens (tem {})".format(chave, min_i, max_i, len(valor)))
                campos = spec.get("campos")
                campos_limites = spec.get("campos_limites", {})
                if campos:
                    for i, item in enumerate(valor):
                        if not isinstance(item, dict) or any(not item.get(c) for c in campos):
                            erros.append("{}[{}] precisa dos campos {}".format(chave, i, ", ".join(campos)))
                            continue
                        for campo, lim in campos_limites.items():
                            v = str(item.get(campo, ""))
                            if len(v) > lim:
                                avisos.append("{}[{}] {} excede {} caracteres".format(chave, i, campo, lim))

        if tipo == "url" and spec.get("auto_corrigir_protocolo") and not URL_RE.match(str(valor)):
            v = str(valor)
            if "://" in v:
                # ja tem um esquema, so que invalido (typo estrutural, ex.
                # "ttps://..."). Corrigir aqui produziria protocolo duplicado
                # ("https://ttps://...") -- bloqueia em vez de adivinhar.
                erros.append("{} invalida: {}".format(chave, v))
            else:
                v_limpo = v.lstrip("/")
                if "." in v_limpo:
                    candidato = "https://" + v_limpo
                    params[chave] = candidato
                    avisos.append("{} sem protocolo -> corrigido para {}".format(chave, candidato))
                else:
                    erros.append("{} invalida: {}".format(chave, v))

        if tipo == "cor":
            pattern = spec.get("pattern")
            if pattern and not re.match(pattern, str(valor)):
                fallback = spec.get("padrao")
                if fallback:
                    avisos.append("{} invalida '{}' -> fallback para {}".format(chave, valor, fallback))
                    params[chave] = fallback
                else:
                    erros.append("{} invalida '{}' e schema nao declara 'padrao' para fallback".format(chave, valor))

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

    schema = load_schema(template_name) or {"variaveis": {}}

    # Validar
    erros, avisos = validar(params, schema)

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

    # Aplicar defaults literais declarados no schema (campo "padrao")
    variaveis = schema.get("variaveis", {})
    for chave, spec in variaveis.items():
        if chave in DEFAULTS_DINAMICOS:
            continue
        padrao = spec.get("padrao")
        if padrao is not None:
            params.setdefault(chave, padrao)

    # Defaults dinamicos: o schema documenta a intencao em prosa
    # ("(ano atual)", "(derivado de SUBTITULO)"), o computo mora aqui
    # porque nao ha como expressar isso como literal em JSON estatico.
    if "ANO" in variaveis:
        params.setdefault("ANO", date.today().year)
    if "META_DESCRICAO" in variaveis:
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
    slug_key = schema.get("slug_campo", DEFAULT_SLUG_CAMPO)
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
