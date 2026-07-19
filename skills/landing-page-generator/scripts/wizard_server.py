#!/usr/bin/env python3
"""
wizard_server.py - Servidor local do wizard visual (Fase 5).

Uso:
    python scripts/wizard_server.py [--port 8765] [--host 127.0.0.1]

Serve assets/wizard/ (a interface) e expoe dois endpoints que chamam
generate.py de verdade -- preview e geracao final usam o MESMO codigo
que o CLI (validar/aplicar_defaults/renderizar/gerar), sem reimplementar
nenhuma regra em JS. So' entende os templates que TEMPLATES_DISPONIVEIS
lista; roda em localhost, nao e' um servidor de producao.

Endpoints:
    GET  /api/schema?template=<nome>   -> devolve template.json
    POST /api/preview  {template,params} -> {erros, avisos, html}
    POST /api/gerar    {template,params} -> resultado de generate.gerar()
"""
import json
import sys
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate  # reaproveita load_schema/load_template/validar/aplicar_defaults/renderizar/gerar

SKILL_DIR = generate.SKILL_DIR
WIZARD_DIR = SKILL_DIR / "assets" / "wizard"
OUTPUT_WIZARD_DIR = SKILL_DIR / "output" / "wizard"
TEMPLATES_DISPONIVEIS = {"landing-page", "proposta"}

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
}


class WizardHandler(BaseHTTPRequestHandler):
    def _enviar_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    @staticmethod
    def _template_valido(nome):
        return nome in TEMPLATES_DISPONIVEIS

    def do_GET(self):
        parsed = urlparse(self.path)
        caminho = parsed.path

        if caminho == "/api/schema":
            qs = parse_qs(parsed.query)
            template = (qs.get("template") or ["landing-page"])[0]
            if not self._template_valido(template):
                self._enviar_json(400, {"erro": "template desconhecido: {}".format(template)})
                return
            schema = generate.load_schema(template)
            if schema is None:
                self._enviar_json(404, {"erro": "schema nao encontrado para {}".format(template)})
                return
            self._enviar_json(200, schema)
            return

        if caminho == "/" or caminho == "":
            caminho = "/index.html"

        # Static file serving restrito a assets/wizard/ -- impede path
        # traversal (../../) e acesso a qualquer coisa fora dessa pasta.
        destino = (WIZARD_DIR / caminho.lstrip("/")).resolve()
        try:
            destino.relative_to(WIZARD_DIR.resolve())
        except ValueError:
            self.send_error(403, "Fora de assets/wizard/")
            return
        if not destino.exists() or not destino.is_file():
            self.send_error(404, "Nao encontrado: {}".format(caminho))
            return

        ext = destino.suffix
        content_type = CONTENT_TYPES.get(ext, "application/octet-stream")
        body = destino.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            corpo = json.loads(raw.decode("utf-8")) if raw else {}
        except json.JSONDecodeError:
            self._enviar_json(400, {"erro": "JSON invalido no corpo da requisicao"})
            return

        template = corpo.get("template", "landing-page")
        params = corpo.get("params", {})
        if not isinstance(params, dict):
            self._enviar_json(400, {"erro": "'params' deve ser um objeto"})
            return
        if not self._template_valido(template):
            self._enviar_json(400, {"erro": "template desconhecido: {}".format(template)})
            return

        if parsed.path == "/api/preview":
            self._preview(template, params)
            return

        if parsed.path == "/api/gerar":
            resultado = generate.gerar(dict(params), template, OUTPUT_WIZARD_DIR / template)
            status = 200 if resultado["status"] == "sucesso" else 422
            self._enviar_json(status, resultado)
            return

        self.send_error(404, "Endpoint desconhecido: {}".format(parsed.path))

    def _preview(self, template, params):
        schema = generate.load_schema(template) or {"variaveis": {}}
        params_copia = dict(params)
        erros, avisos = generate.validar(params_copia, schema)

        html = None
        if not erros:
            try:
                tpl = generate.load_template(template)
            except FileNotFoundError as e:
                self._enviar_json(404, {"erro": str(e)})
                return
            generate.aplicar_defaults(params_copia, schema)
            html = generate.renderizar(tpl, params_copia)

        self._enviar_json(200, {"erros": erros, "avisos": avisos, "html": html})

    def log_message(self, fmt, *args):
        print("[wizard] {}".format(fmt % args))


def main():
    parser = argparse.ArgumentParser(description="Servidor local do wizard visual (Fase 5)")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    OUTPUT_WIZARD_DIR.mkdir(parents=True, exist_ok=True)
    servidor = HTTPServer((args.host, args.port), WizardHandler)
    print("Wizard rodando em http://{}:{}/  (Ctrl+C para parar)".format(args.host, args.port))
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
