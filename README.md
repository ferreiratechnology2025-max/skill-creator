# 🚀 Skill Creator

**Agente Criador de Skills Multi-Plataforma**

Transforme descrições de processos repetitivos em skills estruturadas para Claude Code, Codex (OpenAI), OpenCode e ferramentas similares.

---

## ✨ O que faz

- **Modo 1**: Captura o que você acabou de fazer no chat e transforma em skill
- **Modo 2**: Cola um fluxo de trabalho existente e estrutura automaticamente
- **Modo 3**: Descreve uma ideia vaga e o agente faz perguntas até ter clareza

Cada skill gerada passa por **QA automático com 10 checks** e inclui:
- `SKILL.md` com workflow, exemplos e edge cases
- `evals.json` com casos de teste
- Instruções de instalação multi-plataforma

---

## 📁 Estrutura

```
skill-creator/
├── SKILL.md                        # A skill em si
├── wizard.html                     # Wizard visual (offline, no navegador)
├── install.sh                      # Instalador multi-plataforma
├── CHANGELOG.md                    # Histórico de versões
├── evals/
│   └── evals.json                  # 10 casos de teste
└── references/
    ├── skill-anatomy.md            # Template de anatomia de uma skill
    └── guia-refinamento.md         # Guia de refinamento pós-deploy
```

---

## 🚀 Instalação

### Opção 1: One-liner (recomendado)

```bash
curl -fsSL https://raw.githubusercontent.com/ferreiratechnology2025-max/skill-creator/main/install.sh | bash
```

O script detecta automaticamente:
- Claude Code (`~/.claude/skills/`)
- Codex (`~/.codex/skills/`)
- OpenCode (`~/.config/opencode/skills/`)
- OpenClaw (`~/.openclaw/skills/`)

### Opção 2: Manual

```bash
git clone https://github.com/ferreiratechnology2025-max/skill-creator.git
cd skill-creator
bash install.sh
```

### Opção 3: Wizard Visual (sem terminal)

Abra `wizard.html` no navegador. Funciona 100% offline — navegue pelos 4 passos, preencha os campos e baixe os arquivos prontos.

---

## 🎯 Como Usar

### No Agente (Claude Code / Codex / OpenCode)

```
/criar-skill
```

Ou descreva diretamente:

```
/criar-skill quero algo que me ajude a gerar relatório de vendas semanal
```

### Skill: Landing Page Generator

Para gerar landing pages de PMEs:

```
/criar-skill crie uma landing page para a clínica OdontoSorriso em Goiania, whatsapp 62999999999
```

Ou execute diretamente:

```bash
cd skills/landing-page-generator
python scripts/generate.py params.json
```

### Skill: Site Institucional

Para gerar um site multi-página para um negócio local:

```
cria um site institucional de 5 páginas para a clínica OdontoSorriso
```

Todo dado factual sem fonte real (telefone, endereço, CRO/CNPJ, preços,
equipe, contagens) sai marcado com `<!-- PLACEHOLDER fonte: nenhuma -->`
— nunca formatado como se fosse verificado. Ver o exemplo canônico em
`skills/site-institucional/examples/odontosorriso/` e rodar o QA:

```bash
python skills/site-institucional/scripts/check.py caminho/para/pagina.html
```

### No Wizard Visual

1. Abra `wizard.html` no navegador
2. Escolha um template da biblioteca (6 exemplos) ou comece do zero
3. Preencha: input, processo, output, gatilhos, edge cases
4. Gere SKILL.md + evals.json
5. Baixe os arquivos ou copie para a pasta de skills

---

## 📚 Biblioteca de Skills

### Skills do Projeto Principal

| Skill | Descrição |
|-------|-----------|
| 🏗️ Skill Creator | Agente criador de skills (esta skill) |
| 🎯 LeadFlow Brasil | Geração e outreach de leads B2B |
| 📊 Relatório de Vendas | CSV → relatório por região |
| 🔍 Análise de Concorrentes | Compara preços e features |
| 💬 Responder Comentários | Instagram/LinkedIn no tom da marca |
| 📝 Posts LinkedIn | Vídeo/texto → post engajador |
| 📄 Emissão de NF | Automatiza NF-e |

### Skills de Terceiros (subdiretório `skills/`)

| Skill | Descrição |
|-------|-----------|
| 🌐 Landing Page Generator | Gera landing pages de conversão para PMEs |
| 🏢 Site Institucional | Gera site multi-página (Início, Sobre, Serviços, Equipe, Contato) para negócio local, com regra de proveniência: todo claim factual sem dado real é marcado como placeholder |

---

## 🔍 QA Automático (10 Checks)

Toda skill gerada é validada automaticamente:

1. ✅ Nome em kebab-case
2. ✅ Descrição clara (1-2 frases)
3. ✅ Gatilhos específicos
4. ✅ Passos numerados e imperativos
5. ✅ Exemplos reais de entrada/saída
6. ✅ Mínimo 2 edge cases
7. ✅ Zero credenciais expostas
8. ✅ evals.json com 2+ casos
9. ✅ Pré-requisitos documentados
10. ✅ Plataforma definida

---

## 🛡️ Regras Invioláveis

- NUNCA expor credenciais, tokens ou senhas no SKILL.md
- SEMPRE usar exemplos reais, nunca genéricos
- SEMPRE documentar edge cases (mínimo 2)
- SEMPRE gerar evals.json com testes
- NUNCA criar skill monolítica (>10 passos)

---

## 📖 Documentação

- [`references/skill-anatomy.md`](references/skill-anatomy.md) — Template completo de SKILL.md
- [`references/guia-refinamento.md`](references/guia-refinamento.md) — Como melhorar skills após deploy
- [`CHANGELOG.md`](CHANGELOG.md) — Histórico de versões

---

## 🔄 Multi-Plataforma

| Plataforma | Path de Skills | Compatível |
|------------|----------------|------------|
| Claude Code | `~/.claude/skills/` | ✅ Nativo |
| Codex (OpenAI) | `~/.codex/skills/` | ✅ Nativo |
| OpenCode | `~/.config/opencode/skills/` | ✅ Nativo |
| OpenClaw | `~/.openclaw/skills/` | ✅ Nativo |
| Cursor | `.cursor/skills/` | ⚠️ Adaptar |

---

## 🧪 Testar

```bash
# Verificar se a skill foi instalada
ls ~/.claude/skills/criador-de-skills/

# Ver conteúdo
cat ~/.claude/skills/criador-de-skills/SKILL.md

# Testar evals
cat ~/.claude/skills/criador-de-skills/evals/evals.json
```

---

## 🤝 Contribuir

1. Crie uma skill usando o wizard
2. Teste com dados reais por 1 semana
3. Documente refinamentos no CHANGELOG
4. Envie um PR com a skill para a biblioteca

---

## 📄 Licença

MIT — Livre para usar, modificar e distribuir.

---

**Feito por [Romel Ferreira](https://github.com/ferreiratechnology2025-max)** | Transição de Construtor → Arquiteto
