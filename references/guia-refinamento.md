# Guia de Refinamento Pós-Deploy

## Por que skills não saem perfeitas na primeira vez

Isso é **normal e esperado**. Uma skill é um modelo mental do processo — e modelos mentais precisam de iteração para refletir a realidade.

## Ciclo de Refinamento

```
Deploy → Testar com input real → Identificar falha → Corrigir SKILL.md → Atualizar evals → Re-testar
```

## Como Identificar Problemas

### 1. A skill não é ativada quando deveria
**Causa provável:** Gatilhos vagos ou incompletos

**Solução:**
```markdown
# Antes (ruim)
## Gatilhos
- "relatório"

# Depois (bom)
## Gatilhos
- "gerar relatório de vendas"
- "relatório semanal"
- "vendas por região"
- "exportar dados de vendas"
```

### 2. A skill executa mas o resultado está errado
**Causa provável:** Passos ambíguos ou ordem incorreta

**Solução:**
```markdown
# Antes (ruim)
## Workflow
1. Processar dados
2. Gerar relatório

# Depois (bom)
## Workflow
1. Ler CSV e validar colunas obrigatórias
2. Agrupar registros por coluna 'região'
3. Calcular soma da coluna 'valor' por grupo
4. Ordenar por total decrescente
5. Gerar gráfico de barras com matplotlib
6. Exportar PDF em landscape
```

### 3. A skill falha em cenários específicos
**Causa provável:** Edge cases não documentados

**Solução:**
```markdown
## Edge Cases
- **CSV vazio**: Retornar "Sem dados para o período" e não gerar PDF
- **Coluna 'região' ausente**: Perguntar usuário qual coluna usar como região
- **Valores negativos**: Alertar e pedir confirmação antes de incluir no total
- **Encoding incorreto (acentos)**: Forçar UTF-8 na leitura do arquivo
```

### 4. A skill é ativada em momentos errados
**Causa provável:** Descrição muito genérica

**Solução:**
```markdown
# Antes (ruim)
description: Ajuda com relatórios

# Depois (bom)
description: Gera relatório de vendas por região a partir de CSV. 
Use quando o usuário pedir relatórios de vendas, dados semanais, 
ou análise de performance regional.
```

## Template de Registro de Mudanças

Adicione ao final do SKILL.md:

```markdown
## Changelog

### 2026-06-01 - v1.0
- Deploy inicial

### 2026-06-03 - v1.1
- FIX: Adicionado tratamento para CSV vazio
- FIX: Corrigido gatilho "relatório" → "relatório de vendas"
- ADD: Novo edge case para valores negativos

### 2026-06-07 - v1.2
- FIX: Encoding UTF-8 forçado na leitura
- ADD: Exemplo de entrada com acentos
- UPD: Workflow passo 3 agora valida dados antes de somar
```

## Como Atualizar evals.json

Sempre que corrigir um bug, adicione um teste:

```json
[
  {
    "name": "caso_feliz",
    "input": "relatorio-vendas.csv com 50 registros",
    "expected_output": "PDF gerado com gráfico e 5 regiões"
  },
  {
    "name": "csv_vazio",
    "input": "arquivo.csv com apenas header, sem dados",
    "expected_output": "Mensagem 'Sem dados para o período', nenhum PDF gerado"
  },
  {
    "name": "encoding_acentos",
    "input": "CSV com regiões 'São Paulo', 'Goiás', 'Pará'",
    "expected_output": "Relatório correto sem caracteres corrompidos"
  }
]
```

## Métricas de Qualidade da Skill

Acompanhe para saber quando está "pronta":

| Métrica | Meta | Como medir |
|---------|------|------------|
| Taxa de ativação correta | > 90% | Contar vezes que skill foi ativada no contexto certo |
| Taxa de sucesso | > 80% | Contar execuções que terminaram sem intervenção humana |
| Tempo de refinamento | < 5 ciclos | Número de deploys até estabilizar |
| Cobertura de edge cases | > 80% | % de cenários excepcionais documentados vs encontrados |

## Quando Parar de Refinar

Uma skill está "pronta" quando:
- [ ] Executa corretamente em 10/10 testes com dados reais
- [ ] Não é ativada indevidamente em 20 conversas normais
- [ ] Todos os edge cases conhecidos estão documentados
- [ ] Um novo usuário consegue usar sem perguntar como
- [ ] Changelog tem pelo menos 3 entradas (incluindo v1.0)

## Exemplo Completo de Refinamento

### Skill: `gerar-relatorio-vendas`

**v1.0 (deploy)**
- Funcionou para CSV padrão
- Falhou quando CSV tinha colunas em ordem diferente

**v1.1**
- FIX: Adicionado mapeamento de colunas por nome (não por posição)
- ADD: evals.json com caso de colunas em ordem diferente

**v1.2**
- Falhou quando CSV tinha linhas em branco no meio
- FIX: Adicionado filtro de linhas vazias no passo 1
- ADD: Edge case "linhas em branco"

**v1.3**
- Falhou quando valor era string "R$ 1.000,00" em vez de número
- FIX: Adicionado parser de moeda brasileira no passo 3
- ADD: Exemplo de entrada com formato de moeda

**v1.4 (estável)**
- Funcionou em todos os cenários testados
- Nenhuma falha nova em 2 semanas
- Skill considerada "pronta"

## Dica Final

> **Documente cada falha como um presente.**
> Cada bug encontrado é uma oportunidade de tornar a skill mais robusta para sempre.
> Skills que passaram por 3-5 ciclos de refinamento são significativamente mais confiáveis que skills "perfeitas" na primeira tentativa.
