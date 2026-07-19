# Anatomia de uma Skill

## Estrutura Mínima

```
skill-nome-da-skill/
├── SKILL.md              # Obrigatório
└── evals/
    └── evals.json        # Obrigatório (skill sem fronteira ambígua com outra)
```

Para skills com risco real de confusão de acionamento com uma skill vizinha
(ex. `landing-page-generator` vs `site-institucional`), separar em duas
superfícies — ver "Duas Superfícies de Teste" abaixo:

```
skill-nome-da-skill/
└── evals/
    ├── motor.json        # input → output do motor (params corretos)
    └── triggering.json   # prompt → aciona/não aciona (inclui cruzados)
```

## Estrutura Completa (quando necessário)

```
skill-nome-da-skill/
├── SKILL.md              # Workflow, regras, exemplos
├── evals/
│   └── evals.json        # Casos de teste
├── references/           # Documentos de apoio
│   ├── guia-de-estilo.md
│   ├── especificacao-api.md
│   └── exemplos-reais/
├── scripts/              # Código executável
│   ├── gerar-relatorio.py
│   ├── validar-dados.js
│   └── utils/
└── assets/               # Arquivos estáticos
    ├── template-email.html
    ├── logo.png
    └── fontes/
```

## SKILL.md - Seções Obrigatórias

### 1. Frontmatter (YAML)
```yaml
---
name: nome-da-skill
description: Descrição clara do que faz e quando ativar
---
```

### 2. Título
```markdown
# skill-nome-da-skill
```

### 3. Descrição
- 1-2 frases
- Deixar claro o valor entregue

### 4. Gatilhos
- Lista de comandos/frases que ativam a skill
- Ordenar do mais comum ao menos comum

### 5. Pré-requisitos
- Dependências técnicas
- Arquivos necessários
- Variáveis de ambiente

### 6. Workflow
- Passos numerados
- Imperativos ("Execute", "Valide", "Gere")
- Máximo 10 passos principais

### 7. Exemplos
- Mínimo 1 exemplo real
- Input e output separados
- Usar blocos de código

### 8. Edge Cases
- Mínimo 2 cenários excepcionais
- Sempre incluir: "o que fazer quando falha"

### 9. Regras Invioláveis
- Máximo 5 regras
- Focadas em segurança e qualidade

## SKILL.md - Seções Opcionais

### Multi-Plataforma
```markdown
## Multi-Plataforma
- Claude Code: ~/.claude/skills/
- Codex: ~/.codex/skills/
- OpenCode: ~/.config/opencode/skills/
```

### Métricas de Sucesso
```markdown
## Métricas
- Leads/dia: meta 30+
- Taxa de conversão: meta > 5%
```

### Refinamento
```markdown
## Refinamento Pós-Deploy
1. Testar com input real
2. Identificar falhas
3. Corrigir SKILL.md
4. Atualizar evals.json
```

## Duas Superfícies de Teste

Uma skill tem dois tipos de comportamento distintos, e cada um exige seu
próprio eval — misturá-los num `evals.json` só funciona enquanto a skill
não tem vizinha ambígua no catálogo (ver `landing-page-generator` vs
`site-institucional`, Cenário C de `RELATORIO_FASE4.5.md`):

1. **Motor** (`evals/motor.json`): dado um input estruturado (params,
   dados de negócio), o motor produz o output correto? Testa o código que
   renderiza/gera. Formato: `params.json`-like, com `expected` de sucesso
   ou bloqueio.
2. **Triggering** (`evals/triggering.json`): dado um prompt em linguagem
   natural, a skill certa é acionada — e as vizinhas não? Testa o
   frontmatter/`description`, não o motor. Sempre incluir casos cruzados:
   um prompt que deveria acionar a skill vizinha e não esta, e vice-versa.

Não duplicar cenários de triggering num formato feito para o motor (ou
vice-versa) — formato incompatível reaproveitado parece cobertura e não
roda. Se a skill não tem vizinha ambígua, um único `evals.json` no formato
"motor" ou "triggering" (o que fizer sentido para a skill) é suficiente;
a separação em dois arquivos só se justifica quando os dois tipos de teste
coexistem de fato.

## evals.json / motor.json - Estrutura

```json
[
  {
    "name": "caso_feliz",
    "input": "descrição do input de teste",
    "expected_output": "descrição do resultado esperado"
  },
  {
    "name": "edge_case_1",
    "input": "cenário excepcional",
    "expected_output": "como a skill deve lidar"
  }
]
```

### Regras dos Evals
- Mínimo 2 casos por skill
- 1 caso feliz (fluxo normal)
- 1+ edge cases
- Nomes descritivos
- Inputs e outputs como strings

## triggering.json - Estrutura

Mesmo formato de `{name, input, expected_output}`, mas `input` é sempre um
prompt em linguagem natural e `expected_output` declara explicitamente
qual skill aciona (ou nenhuma) e por quê:

```json
[
  {
    "name": "cross_scenario_vizinha_nao_aciona",
    "input": "prompt que deveria acionar a skill vizinha, não esta",
    "expected_output": "Aciona <skill-vizinha>. Esta skill NÃO é acionada — motivo específico do frontmatter/semântica que evita a ambiguidade."
  }
]
```

### Regras do Triggering
- Mínimo 1 caso cruzado por skill vizinha ambígua conhecida
- `expected_output` sempre nomeia a skill esperada, nunca só "aciona"/"não aciona"
- Triggering só é validado de verdade com sessão real rodando o prompt —
  casos em disco documentam a expectativa, não substituem a checagem ao vivo

## Nomenclatura

### Nome da Skill
- kebab-case (minúsculas, hífens)
- Máximo 5 palavras
- Descritivo e único
- Exemplos:
  - ✅ `gerar-relatorio-vendas`
  - ✅ `analisar-concorrentes`
  - ❌ `GerarRelatorio` (camelCase)
  - ❌ `skill_1` (genérico)
  - ❌ `minha-skill-incrivel` (vago)

### Nome dos Arquivos
- `SKILL.md` (sempre maiúsculo)
- `evals.json` (sempre minúsculo)
- Scripts: kebab-case ou snake_case

## Anti-Padrões (Não Faça)

1. **Não expor credenciais**
   ```markdown
   ❌ API_KEY=sk-abc123
   ✅ API_KEY (definir em .env)
   ```

2. **Não usar linguagem vaga**
   ```markdown
   ❌ "Processar os dados"
   ✅ "Agrupar vendas por região e calcular totais"
   ```

3. **Não omitir exemplos**
   ```markdown
   ❌ [Sem seção de exemplos]
   ✅ Exemplo real com input e output
   ```

4. **Não criar skill monolítica**
   ```markdown
   ❌ 20 passos em 1 skill
   ✅ Dividir em 3 skills de 6-7 passos cada
   ```

5. **Não ignorar edge cases**
   ```markdown
   ❌ [Sem edge cases]
   ✅ Mínimo 2 cenários documentados
   ```

## Checklist Final

Antes de considerar uma skill "pronta":

- [ ] Nome em kebab-case
- [ ] Frontmatter com name e description
- [ ] Descrição clara (1-2 frases)
- [ ] Gatilhos específicos listados
- [ ] Passos numerados e imperativos
- [ ] Exemplo real de entrada
- [ ] Exemplo real de saída
- [ ] Mínimo 2 edge cases
- [ ] Zero credenciais expostas
- [ ] evals/motor.json (ou evals.json) com 2+ casos
- [ ] Se há skill vizinha ambígua no catálogo: evals/triggering.json com caso(s) cruzado(s)
- [ ] Pré-requisitos documentados
- [ ] Regras invioláveis definidas
