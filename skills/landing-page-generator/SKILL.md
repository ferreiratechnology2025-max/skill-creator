---
name: landing-page-generator
description: |
  Gera landing pages profissionais a partir de dados de leads/empresas.
  Use sempre que o usuario pedir para criar, gerar ou montar uma landing page,
  pagina de captura, pagina de vendas ou LP para um negocio, cliente ou lead —
  mesmo que ele so descreva o negocio em texto livre.
  Tambem use quando o usuario fornecer dados de um lead/empresa em formato
  estruturado ou nao, perguntando sobre criacao de pagina, conversao, ou
  presenca digital.
---

# Landing Page Generator

Transforma dados de um negocio em uma landing page publicavel em segundos, usando um template parametrizado com contrato explicito de variaveis. O fluxo e' deterministico: os mesmos parametros sempre produzem a mesma pagina.

## 🖥️ Plataforma Compativel

| Plataforma | Compativel | Path |
|------------|------------|------|
| Claude Code | ✅ | `~/.claude/skills/` |
| Codex (OpenAI) | ✅ | `~/.codex/skills/` |
| OpenCode | ✅ | `~/.config/opencode/skills/` |
| OpenClaw | ✅ | `~/.openclaw/skills/` |

## 📋 Pre-requisitos

- Python 3.8 ou superior
- Estrutura de diretorios:
  ```
  landing-page-generator/
  ├── assets/templates/landing-page/
  │   ├── index.html    # Template com {{VARS}}
  │   └── template.json # Contrato de variaveis
  ├── scripts/
  │   ├── generate.py   # Motor de renderizacao
  │   └── check.py      # QA validator
  └── evals/evals.json  # Casos de teste
  ```

## Arquitetura

```
parametros (JSON)
      ↓
scripts/generate.py   ← motor deterministico (valida + renderiza)
      ↓
output/<slug>/index.html + params.json
      ↓
scripts/check.py      ← QA independente (8 checks)
```

O template vive em `assets/templates/{nome}/` e seu contrato de variaveis esta em `template.json` (leia-o antes de montar os parametros). `generate.py` deriva toda a validacao desse arquivo em runtime — nao ha copia hardcoded de limites/obrigatoriedade em codigo (ver `scripts/test_schema_reflete.py`, que prova isso por comportamento).

## 🧙 Wizard Visual (Fase 5)

Interface visual local para preencher os parametros com pre-visualizacao ao vivo, sem editar JSON a mao. Roda um servidor local que reaproveita `generate.py` de verdade (mesmo `validar`/`renderizar`/`gerar` do CLI) — o preview no navegador nunca reimplementa a validacao em JS.

```bash
python scripts/wizard_server.py --port 8765
# abrir http://127.0.0.1:8765/ no navegador
```

O formulario e' construido dinamicamente a partir do `template.json` do template selecionado (`landing-page` ou `proposta`) — trocar um limite no schema muda o formulario e a validacao ao mesmo tempo, sem tocar em `assets/wizard/index.html`. Servidor local apenas (`127.0.0.1`), sem autenticacao — nao e' para expor em rede.

```
scripts/wizard_server.py   ← http.server stdlib, reaproveita generate.py
assets/wizard/index.html   ← formulario + iframe de preview, le /api/schema
```

Endpoints: `GET /api/schema?template=<nome>`, `POST /api/preview`, `POST /api/gerar` (grava em `output/wizard/<template>/<slug>/`, mesmo formato do CLI).

## 📝 Exemplos de Uso

### Gerar Landing Page
```bash
python scripts/generate.py params.json
```

### Gerar com Template Especifico
```bash
python scripts/generate.py --template proposta proposta.json
```

### Especificar Diretorio de Saida
```bash
python scripts/generate.py params.json --output output/prod/
```

### Rodar QA
```bash
python scripts/check.py output/<slug>/index.html
```

### Testar Todos os Casos
```bash
# Modo batch - executa todos os JSON em evals/inputs/
python scripts/generate.py --test-all
```

### Executar Suite de Testes Completa
```bash
# Windows
test.bat

# Linux/Mac
chmod +x test.sh && ./test.sh
```

## Fluxo de trabalho

1. **Colete os parametros.** Extraia da conversa: nome do negocio, cidade, proposta de valor, CTA e link (normalmente WhatsApp). Se faltar algo obrigatoria, pergunte — nao invente telefone, endereco ou nome. Beneficios e copy voce PODE redigir com base no segmento do negocio.

2. **Monte o `params.json`** seguindo `assets/templates/landing-page/template.json`. Exemplo minimo:

```json
{
  "NOME_NEGOCIO": "Clinica Sorriso Vivo",
  "TITULO_HERO": "Seu sorriso novo em ate 30 dias",
  "SUBTITULO": "Avaliacao gratuita com especialistas em implantes e estetica dental.",
  "CTA_TEXTO": "Agendar avaliacao",
  "LINK_CTA": "https://wa.me/5562999990000?text=Quero%20agendar",
  "CIDADE": "Goiania",
  "BENEFICIOS": [
    {"titulo": "Avaliacao gratuita", "descricao": "Diagnostico completo sem custo e sem compromisso."},
    {"titulo": "Parcelamento facilitado", "descricao": "Planos que cabem no seu orcamento, em ate 24x."},
    {"titulo": "Tecnologia digital", "descricao": "Escaneamento 3D e planejamento digital do sorriso."}
  ]
}
```

3. **Gere:**

```bash
python scripts/generate.py params.json
```

4. **Rode o QA (sempre, mesmo que a geracao pareca ok):**

```bash
python scripts/check.py output/<slug>/index.html
```

5. **Entregue** o `output/<slug>/` completo. O `params.json` arquivado junto permite regenerar ou ajustar a pagina depois.

## Regras de copy

- TITULO_HERO: beneficio concreto + prazo ou diferencial ("Seu sorriso novo em ate 30 dias"), nunca generico ("Bem-vindo ao nosso site").
- SUBTITULO: expande o hero com credibilidade ou oferta; max. 200 caracteres.
- CTA_TEXTO: verbo no infinitivo + objeto ("Agendar avaliacao", "Pedir orcamento"); nunca "Clique aqui".
- BENEFICIOS: 3 a 10 itens, cada um respondendo "por que escolher este negocio?" — especificos do segmento, não clichês universais.
- Tudo em portugues brasileiro, tom direto, sem superlativo vazio ("o melhor da regiao").

## ⚠️ Edge Cases Tratados

1. **Caracteres especiais no nome da empresa**: `Açaí & Cia` → slug `acai-cia` (normalizacao automatica)
2. **Cores customizadas invalidas**: Fallback para paleta padrao (#2563eb, #1e3a8a)
3. **Título muito curto/longo**: Bloqueia geracao se <10 ou >80 caracteres
4. **Telefone ausente**: Bloqueia geracao (nunca inventar dados)
5. **URL sem protocolo**: Adiciona `https://` automaticamente

## Regras inviolaveis

- NUNCA inventar dados factuais do negocio (telefone, endereco, CNPJ, precos, promocoes não informadas).
- NUNCA incluir credenciais, tokens ou chaves nos parametros ou no HTML.
- SEMPRE rodar `check.py` antes de entregar.
- SEMPRE arquivar `params.json` junto ao HTML gerado.

## Deploy

A pagina e' um HTML unico sem dependencias externas. Sobe direto em Cloudflare R2/Pages, S3+CloudFront, Netlify ou qualquer host estatico — basta copiar `index.html`. Para o pipeline de outreach, o `output/<slug>/` mapeia 1:1 com o path do bucket.
