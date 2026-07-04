# skill-criador-de-skills

## Descrição
Agente especializado em transformar descrições de processos repetitivos em skills estruturadas (SKILL.md + evals.json) para Claude Code, Codex, OpenCode e ferramentas similares. Realiza QA automático com 10 checks, gera exemplos reais e documenta edge cases.

## Gatilhos
Ative quando o usuário pedir:
- "/criar-skill" ou "criar uma skill"
- "automatizar [processo]"
- "gerar SKILL.md para [tarefa]"
- "criar habilidade de [ação]"
- "transformar isso em uma skill"
- "documentar este processo como skill"

## Pré-requisitos
- Python 3.10+ (para scripts auxiliares)
- Navegador web (para wizard visual)
- Uma das plataformas: Claude Code, Codex (OpenAI), OpenCode, ou similar
- Pasta de skills configurada (detectada automaticamente pelo install.sh)

## Workflow

### Modo 1: Capturar sessão recente
1. Analisar o histórico da conversa atual
2. Identificar os passos executados pelo usuário
3. Extrair: input, processo, output, gatilhos
4. Gerar SKILL.md e evals.json
5. Executar QA automático (10 checks)
6. Apresentar para revisão do usuário
7. Fazer deploy na pasta de skills detectada

### Modo 2: Colar fluxo de trabalho
1. Receber texto descrevendo o processo
2. Estruturar em: input → processo → output → gatilhos
3. Gerar SKILL.md e evals.json
4. Executar QA automático (10 checks)
5. Apresentar para revisão do usuário
6. Fazer deploy na pasta de skills detectada

### Modo 3: Descrever ideia vaga
1. Fazer perguntas estruturadas até ter clareza:
   - "O que você fornece como entrada?"
   - "Quais são os passos exatos do processo?"
   - "Qual é o resultado perfeito no final?"
   - "Quando esta skill deve ser ativada?"
   - "O que pode dar errado?"
2. Consolidar respostas em workflow estruturado
3. Gerar SKILL.md e evals.json
4. Executar QA automático (10 checks)
5. Apresentar para revisão do usuário
6. Fazer deploy na pasta de skills detectada

## QA Automático (10 Checks)
Antes de entregar qualquer skill, verificar:
1. **Nome**: kebab-case, descritivo, sem acentos (ex: gerar-relatorio-vendas)
2. **Descrição**: 1-2 frases claras do que faz e quando usar
3. **Gatilhos**: Lista específica de comandos/frases que ativam a skill
4. **Passos**: Numerados, imperativos, sequência lógica clara
5. **Exemplos**: Pelo menos 1 exemplo real de entrada e saída
6. **Edge Cases**: Mínimo 2 cenários excepcionais documentados
7. **Credenciais**: NENHUMA senha/token/chave exposta no arquivo
8. **Evals**: evals.json presente com pelo menos 2 casos de teste
9. **Pré-requisitos**: Dependências, arquivos, variáveis necessárias listadas
10. **Formato**: Estrutura markdown correta, headers hierárquicos

## Estrutura de Saída
```
skill-nome-da-skill/
├── SKILL.md              # Workflow, regras, exemplos, edge cases
└── evals/
    └── evals.json        # Casos de teste (input + expected_output)
```

Opcionais (quando necessário):
```
references/               # Documentos de apoio, especificações
scripts/                  # Código executável (Python, bash)
assets/                   # Templates, fontes, arquivos estáticos
```

## Exemplos

### Exemplo 1: LeadFlow Brasil (referência completa)
**Input:**
```
/criar-skill
Sistema de geração e outreach de leads B2B no Brasil. 
Busca empresas no Google Maps, enriquece contatos, qualifica com scoring,
gera mensagens personalizadas e envia e-mails com retry.
```
**Output esperado:**
```markdown
# skill-leadflow-brasil
## Descrição
Sistema agentic de geração e outreach de leads B2B no Brasil...
## Gatilhos
- "Gerar leads para [segmento] em [cidade]"
- "Executar workflow de busca"
...
## Workflow
1. Planejamento: entender segmento e cidade
2. Busca: executar scraper_maps.py
3. Enriquecimento: executar enricher.py
...
## Edge Cases
- API indisponível: retry com backoff
- E-mail não encontrado: marcar como parcial
...
```

### Exemplo 2: Skill simples (gerar relatório)
**Input:**
```
/criar-skill
Toda sexta eu baixo um CSV de vendas e preciso calcular totais por região
```
**Output esperado:**
```markdown
# skill-gerar-relatorio-vendas-semanal
## Descrição
Gera relatório de vendas por região a partir de CSV semanal...
## Gatilhos
- "Gerar relatório de vendas"
- "Relatório semanal"
...
```

### Exemplo 3: Skill de análise de concorrentes
**Input:**
```
/criar-skill
Analisar preços de concorrentes no site deles e gerar comparativo
```
**Output esperado:**
```markdown
# skill-analisar-concorrentes
## Descrição
Pesquisa preços de concorrentes e gera tabela comparativa...
## Gatilhos
- "Analisar concorrentes de [produto]"
- "Comparar preços"
...
```

## Edge Cases
- **Usuário descreve processo incompleto**: Fazer perguntas até ter clareza, nunca assumir
- **Processo muito complexo (10+ passos)**: Sugerir dividir em 2-3 skills menores
- **Usuário quer credenciais no SKILL.md**: Bloquear e explicar que credenciais vão em .env
- **Plataforma não detectada**: Perguntar explicitamente (Claude Code, Codex, OpenCode?)
- **Skill com nome conflitante**: Verificar se já existe e sugerir renomear
- **Evals insuficientes**: Gerar pelo menos 2 casos, mesmo que o usuário não peça
- **Processo ilegal ou antiético**: Recusar educadamente e explicar o porquê

## Regras Invioláveis
- NUNCA incluir credenciais, tokens, senhas ou chaves API no SKILL.md
- SEMPRE usar exemplos reais, nunca genéricos do tipo "exemplo de entrada"
- SEMPRE documentar o que pode dar errado (mínimo 2 edge cases)
- SEMPRE gerar evals.json com pelo menos 2 casos de teste
- NUNCA criar skill com mais de 10 passos principais (dividir se necessário)
- SEMPRE validar nome em kebab-case antes de entregar
- SEMPRE perguntar plataforma alvo se não detectada automaticamente

## Multi-Plataforma

### Claude Code
- Skills em: `~/.claude/skills/`
- Ativação: digitar o nome da skill ou gatilho no chat
- Formato: SKILL.md padrão

### Codex (OpenAI)
- Skills em: `~/.codex/skills/` (ou equivalente)
- Ativação: via comando ou contexto
- Formato: SKILL.md padrão + possível adaptação de gatilhos

### OpenCode
- Skills em: conforme documentação da ferramenta
- Ativação: via interface ou comando
- Formato: SKILL.md padrão

### Outras ferramentas
- Adaptar path de instalação conforme documentação
- Manter estrutura SKILL.md + evals.json como padrão
- Gatilhos podem ser adaptados para comandos específicos da ferramenta

## Refinamento Pós-Deploy
1. Testar a skill com input real
2. Identificar falhas ou comportamentos inesperados
3. Editar SKILL.md para corrigir instruções
4. Adicionar novos edge cases descobertos
5. Atualizar evals.json com novos casos de teste
6. Versionar mudanças (adicionar data no header)

## Métricas de Qualidade da Skill Gerada
- Completa: todos os 10 checks do QA passaram
- Testável: evals.json cobre cenários principais
- Portátil: funciona em pelo menos 2 plataformas
- Robustá: edge cases documentados e tratados
- Segura: zero credenciais expostas
