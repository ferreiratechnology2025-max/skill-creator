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
├── evals/
│   └── evals.json                  # 10 casos de teste
└── references/
    ├── skill-anatomy.md            # Template de anatomia de uma skill
    └── guia-refinamento.md         # Guia de refinamento pós-deploy
```

---

## 🚀 Instalação

### Opção 1: One-liner (recomendado)

> ⚠️ **Substitua `SEU-USUARIO` pelo seu usuário GitHub antes de executar.**

```bash
curl -fsSL https://raw.githubusercontent.com/SEU-USUARIO/skill-creator/main/install.sh | bash
```

```bash
curl -fsSL https://raw.githubusercontent.com/seu-repo/skill-creator/main/install.sh | bash
```

O script detecta automaticamente:
- Claude Code (`~/.claude/skills/`)
- Codex (`~/.codex/skills/`)
- OpenCode (`~/.config/opencode/skills/`)
- OpenClaw (`~/.openclaw/skills/`)

### Opção 2: Manual

> ⚠️ **Substitua `SEU-USUARIO` pelo seu usuário GitHub antes de executar.**

```bash
git clone https://github.com/SEU-USUARIO/skill-creator.git
cd skill-creator
bash install.sh
```

```bash
git clone https://github.com/seu-repo/skill-creator.git
cd skill-creator
bash install.sh
```

### Opção 3: Wizard Visual (sem terminal)

```bash
open wizard.html
```

Funciona 100% offline. Navegue pelos 4 passos, preencha os campos e baixe os arquivos prontos.

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

### No Wizard Visual

1. Abra `wizard.html` no navegador
2. Escolha um template da biblioteca (24 exemplos) ou comece do zero
3. Preencha: input, processo, output, gatilhos, edge cases
4. Gere SKILL.md + evals.json
5. Baixe os arquivos ou copie para a pasta de skills

---

## 📚 Biblioteca de Templates

O wizard inclui templates prontos:

| Template | Descrição |
|----------|-----------|
| 🎯 LeadFlow Brasil | Geração e outreach de leads B2B |
| 📊 Relatório de Vendas | CSV → relatório por região |
| 🔍 Análise de Concorrentes | Compara preços e features |
| 💬 Responder Comentários | Instagram/LinkedIn no tom da marca |
| 📝 Posts LinkedIn | Vídeo/texto → post engajador |
| 📄 Emissão de NF | Automatiza NF-e |

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

**Feito por Romel Ferreira** | Transição de Construtor → Arquiteto
