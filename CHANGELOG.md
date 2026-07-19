# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.5.0] — 2026-07-19

**Fase 5 (`RELATORIO_FASE4.5.md`)**: interface visual + integração com o motor + preview em tempo real, conforme planejado. Consolida também o gate 2 (validação schema-driven) e as correções de harness que antecederam o wizard — nenhuma delas tinha entrada própria no CHANGELOG, só mensagem de commit.

### Adicionado
- **`scripts/wizard_server.py`**: servidor local (stdlib `http.server`, sem dependências) que reaproveita `generate.py` de verdade — `/api/preview` e `/api/gerar` chamam `validar`/`aplicar_defaults`/`renderizar`/`gerar`, não reimplementam nada em JS. Serve `assets/wizard/` com guarda contra path traversal.
- **`assets/wizard/index.html`**: formulário construído dinamicamente a partir do `template.json` buscado via `/api/schema` — trocar um limite no schema muda o formulário sem tocar no HTML. Preview ao vivo via iframe, suporta os dois templates (`landing-page`, `proposta`).
- **`scripts/generate.py: aplicar_defaults()`**: extraída de `gerar()` para ser reaproveitada pelo wizard sem duplicar a lógica de defaults literais/dinâmicos.

### Corrigido (validação schema-driven — gate 2 da Fase 5, ver `guia-refinamento.md` item 9)
- `generate.py` não tem mais `LIMITES`/`OBRIGATORIAS_LANDING`/`OBRIGATORIAS_PROPOSTA` hardcoded — `validar()` deriva tudo de `template.json`. `load_schema()` existia mas nunca era chamada; agora é o único caminho de leitura de regras.
- Dois gaps de contrato expostos pelo próprio refactor: template `proposta` nunca teve nenhuma regra validada (só presença de campos), e o `{{ANO}}` usado 2x no HTML da proposta nunca esteve declarado no `template.json` dela.
- URL: distingue "sem protocolo" (corrige) de "esquema inválido tipo `ttps://`" (bloqueia — corrigir produziria protocolo duplicado). Cor: bloqueia se schema não declarar `padrao`, em vez de gravar `None` silenciosamente.
- `scripts/test_schema_reflete.py`: teste de regressão permanente, prova por comportamento (muda limite no schema, exige que o motor reflita) — é o próprio experimento que reprovou o motor no gate 2, promovido a guarda.
- **Estágio `[1/4]` de `test.sh`/`test.bat` mascarava regressão real** com `python generate.py --test-all || true` — uma falha de validação genuína (não um bloqueio esperado do `EXPECTED_FAILS`) passava pelos 4 estágios sem ser contada, harness terminava "All 4 stages passed" com uma regressão real dentro. Corrigido: exit code de `--test-all` agora conta para o resultado final.
- `--test-all` também misturava saída de `proposta` e `landing-page` no mesmo diretório, fazendo `check.py` (QA específico de landing-page: CTA, LGPD) reprovar um documento que nunca teve esse contrato. Corrigido: saída em lote separada por template (`output/test-suite/<template>/<slug>`).

## [1.4.0] — 2026-07-19

**Nota sobre versionamento**: o salto de 1.3.0 para 1.4.0 não pula uma versão planejada — 1.3.0 já existia neste CHANGELOG antes desta release, cobrindo trabalho não relacionado (cache/determinismo/batch mode do `generate.py`, ver seção abaixo), commitado no mesmo dia. 1.4.0 é a próxima MINOR livre pelo SemVer, escolhida por esta release adicionar uma skill nova (`site-institucional`), não corrigir a existente.

### Adicionado
- **Nova skill: `site-institucional`** — gera site multi-página (tipicamente 5) para negócio local, com token system de design próprio por briefing e regra de proveniência executável
  - `SKILL.md` com regra inviolável: todo claim de aparência factual (CRO/CNPJ, preço, telefone, endereço, contagem de clientes/anos, promessas operacionais) tem proveniência declarada — `fonte: busca | usuário | placeholder`
  - `scripts/check.py` v2: QA independente com 9 categorias de claim (CRO/CNPJ, preço, telefone, contagem, ano de fundação, prazo em dias úteis, parcelamento, promessa "mesmo dia", duração), janela de 20 linhas entre claim e marcador de proveniência
  - `evals/triggering.json`: 6 casos incluindo cenários cruzados com `landing-page-generator` (cada skill é o teste negativo da outra) e edge case de dados completos fornecidos pelo usuário (`fonte: usuário`, sem placeholder)
- **Site-exemplo canônico**: OdontoSorriso (5 páginas) em `skills/site-institucional/examples/odontosorriso/`, gerado sem nenhum dado real de entrada, 100% dos claims fabricados marcados com `<!-- PLACEHOLDER fonte: nenhuma -->` (10 marcadores só em `equipe.html`, um por card + rodapé) e 5/5 checks passando em todas as páginas com o check v2
- **`references/skill-anatomy.md`**: formaliza as duas superfícies de teste de uma skill — `evals/motor.json` (input→output do motor) e `evals/triggering.json` (prompt→aciona/não aciona, incluindo cruzados) — como estrutura de primeira classe, com regra explícita de que triggering em disco documenta expectativa mas não substitui checagem ao vivo

### Corrigido
- **Gap de marcação no site-exemplo**: auditoria com o `check.py` v1 achou blocos de dado fabricado sem marcador de proveniência (1 card de equipe fora da janela de 20 linhas do marcador de topo; 6 promessas operacionais + "desde 2012" em 5 rodapés, em nenhuma categoria coberta pelo check v1). Corrigido com marcação individual por bloco (Opção A: redundância explícita) e as 5 novas categorias de regex do check v2.
- **Regra de janela vs. cobertura de categoria**: a auditoria separou dois mecanismos de falha distintos — falso-negativo por distância da âncora (janela de 20 linhas insuficiente para blocos espaçados) e categoria de claim sem regex correspondente (o check nunca olhava para essas). Documentado no docstring do `check.py` v2: uma categoria nova de claim factual sem regex correspondente continua passando despercebida até ser adicionada — o check cobre o que foi enumerado, não é exaustivo por construção.

## [1.3.0] — 2026-07-19

### Corrigido
- **Cache removido**: `lru_cache` substituido por carregamento direto (determinismo total)
- **Batch mode corrigido**: `--test-all` agora classifica corretamente edge cases vs erros reais
- **Classificacao de testes**: edge cases marcados como [EDGE], sucesso como [OK], bloqueios como [BLOCKED]
- **Resumo do batch**: mostra Total | Sucesso | Bloqueios esperados | Erros reais

### Adicionado
- **EXPECTED_FAILS**: lista de arquivos que devem falhar (edge cases + proposta_teste + tc_004)
- **lead_real_fluentemax.json**: novo lead ficticio para validacao final
- **test.bat/test.sh**: scripts de teste atualizados com classificacao correta

### Modificado
- **generate.py**: removido `functools.lru_cache`, functions `load_template` e `load_schema` sem cache
- **SKILL.md**: frontmatter ajustado para melhor triggering no Claude Code
- **README.md**: nova secao "Skills de Terceiros" com landing-page-generator

## [1.2.0] — 2026-07-19

### Adicionado
- **Motor multi-template**: suporte a `--template proposta` para gerar paginas diferentes
- **Template proposta-comercial**: segunda prova de conceito com layout diferente
- **Logging estruturado**: replace de prints por logging com niveis DEBUG/INFO/WARNING/ERROR
- **Modo batch `--test-all`**: executa todos os JSON em `evals/inputs/` com resumo
- **Output JSON**: `gerar()` retorna dict com status, slug, errors, warnings
- **Validacao dinamica**: obrigatorias variam por template (NOME_NEGOCIO vs CLIENTE)
- **Renderizacao de listas simples**: suporte a `{{.}}` para arrays de strings
- **Scripts de teste**: `test.bat` (Windows) e `test.sh` (Linux/Mac)
- **Exemplos de uso** adicionados ao SKILL.md

### Modificado
- **template.json v1.1.0**: max_beneficios 3-10 (antes 3-6), cor_padrao azul royal, regras detalhadas
- **generate.py**: refactor completo com funcao `gerar()`, logging, validacao dinamica
- **check.py**: limite title aumentado de 70 para 90 caracteres
- **SKILL.md**: secoes de exemplos de uso adicionadas

## [1.1.0] — 2026-07-19

### Adicionado
- **Nova skill: `landing-page-generator`** — Gera landing pages de conversão para PMEs a partir de template parametrizado
  - Motor de renderização determinístico (`scripts/generate.py`)
  - QA validator independente (`scripts/check.py`) com 8 checks
  - Template HTML único sem dependências externas
  - Contrato de variáveis explícito (`template.json`)
  - 7 casos de teste em `evals/evals.json`
  - Suporte a caracteres especiais, normalização de slug, fallback de cores
  - Compatível com Claude Code, Codex (OpenAI), OpenCode e OpenClaw
- Diretoria `skills/landing-page-generator/` no projeto principal

### Corrigido
- Edge cases expandidos de 3 para 5 no SKILL.md
- Seção de Plataforma adicionada ao SKILL.md
- Pré-requisitos documentados com estrutura de diretórios
- Bugs de encoding Windows (cp1252) corrigidos: replace de ✓, ✗, →, ≤ por ASCII seguro
- Fallback de cores inválidas implementado (antes bloqueava, agora usa defaults)
- Auto-correção de URL sem protocolo implementada (antes bloqueava, agora adiciona https://)
- Limite de tag <title> no check.py aumentado de 70 para 90 caracteres
- Mínimo de 10 caracteres adicionado para TITULO_HERO
- 7 casos de teste validados com 100% de sucesso
- 3 leads reais testados (2 sucesso + 1 bloqueio esperado)

## [1.0.0] — 2025-07-04

### Adicionado
- Wizard visual 100% offline com 4 passos e 6 templates prontos
- Instalador multi-plataforma (`install.sh`) com detecção automática de Claude Code, Codex, OpenCode e OpenClaw
- QA automático com 10 checks de qualidade
- Exemplo completo de referência: LeadFlow Brasil (SKILL.md + 10 evals)
- Documentação de referência: anatomia de skill e guia de refinamento pós-deploy
- Suporte a 3 modos de criação: capturar sessão, colar fluxo, ideia vaga
- Persistência de progresso no wizard via `localStorage`
- Geração de SKILL.md alinhada ao padrão LeadFlow (métricas, refinamento, changelog, regras invioláveis)
- Evals.json gerado com casos de teste específicos e reais

### Corrigido
- Placeholder `seu-repo` substituído por `SEU-USUARIO` nas URLs do README
- Estrutura de evals gerada pelo wizard agora inclui casos de teste reais em vez de placeholders

## [0.1.0] — 2025-06-25

### Adicionado
- Versão inicial do projeto
- SKILL.md principal com workflow de criação de skills
- README.md com instruções de uso
- install.sh com instalação manual e automática
- wizard.html com interface básica de 4 passos
- 10 evals para testar a skill criadora
- references/skill-anatomy.md — template de estrutura
- references/guia-refinamento.md — ciclo de melhoria contínua

---

**Feito por Romel Ferreira** | Transição de Construtor → Arquiteto
 
"## [1.3.1] - 2026-07-19 (Fase 4.5)" 
""  
"### Validado" 
"- **Triggering validado**: Analise empirica do frontmatter confirmou que skill aciona corretamente para prompts de landing page/pagina de vendas e NAO aciona para site institucional/post de Instagram (6/12 corretos - todos dentro do esperado)" 
"- **Causa raiz do proposta_teste documentada**: O bug era de orquestracao do batch mode (nao detecta template automaticamente), nao de validacao. Caso esta no EXPECTED_FAILS com justificativa clara." 
"- **Instalacao comprovada**: Skill instalada em ~/.claude/skills/ com evidencia de arquivos e conteudo do SKILL.md" 
"- **Integridade do contrato confirmada**: template.json inalterado desde v1.1.0 - 0 regras alteradas, 0 limites relaxados, 0 bloqueios removidos" 
"- **Evidencias brutas**: output/instalacao_prova.txt, output/triggering_log.txt, output/causa_raiz_proposta_teste.md, RELATORIO_FASE4.5.md" 
