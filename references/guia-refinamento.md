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

---

## Jurisprudência do Processo de Aceite (2026-07-19)

O que vem acima é o guia genérico. O que vem abaixo não é teórico — é o processo
de aceite que este projeto usou de verdade na construção de `landing-page-generator`
e `site-institucional`, extraído retroativamente da sessão que os produziu. Cada
regra abaixo foi checada contra o repositório antes de entrar aqui; onde a checagem
não bateu, a regra foi corrigida ou marcada como não verificada — porque a regra 8
se aplica a este próprio documento.

### 1. Evidência bruta ou não aconteceu

**A regra**: um relatório de correção não é aceito só porque afirma ter corrigido algo — precisa de evidência que possa ser checada de novo, depois, por outra pessoa (diff, grep, execução).

**Origem**: **não verificável neste repositório.** Uma versão anterior deste guia citava "Fase 3, seção File-mutation verifier" com `sha256sum` e um bug de path `/d/` vs `C:\d\` como origem desta regra. Busca ampla (`grep -rni "file-mutation|resolve_template|sha256"`) não encontrou essa seção em `RELATORIO_FASE3.md` nem em nenhum outro arquivo do projeto. A citação não resistiu ao grep — mantida aqui sem a origem fabricada, porque a regra em si é correta e este é o exemplo mais direto possível de por que ela precisa existir: mesmo uma citação de origem pode ser inventada com aparência de precisão.

### 2. Triggering só existe em sessão real

**A regra**: um teste de "a skill aciona no prompt X" não é validado por leitura de frontmatter — só por rodar o prompt de verdade e observar o que acontece.

**Origem verificável**: `skills/landing-page-generator/RELATORIO_FASE4.md:114,188` — "O frontmatter atual é suficiente... Triggering analisado — frontmatter atual é suficiente" foi o veredito da Fase 4, sem instalação nem sessão ao vivo. Confirmado por grep nesta sessão.

### 3. Transcrição ganha de relato — de agente e de humano

**A regra**: em disputa sobre o que aconteceu numa sessão, grep na transcrição resolve — não importa se a alegação é de um agente ou de um humano.

**Origem verificável**: nesta mesma sessão, uma única checagem de transcrição corrigiu três alegações ao mesmo tempo — a hipótese de mistura de fontes (não havia fontes), a lembrança de "vi ele acionando" (era `Skill(frontend-design)`, não busca), e um relatório citando o nome "Odontofarris" (não aparece em nenhum arquivo). Nenhuma das três resistiu a `grep`.

### 4. Explícito ganha de inferido — e o relatório que documenta a correção também pode ficar desatualizado

**A regra**: prefira um campo declarado explicitamente a uma heurística de inferência. E: um relatório que documenta "a correção foi X" descreve o estado do código *naquele momento* — não é garantia de que X ainda é a correção vigente.

**Origem verificável**: `skills/landing-page-generator/scripts/generate.py:65-75`, função `resolve_template(params)`: usa o campo explícito `"template"` se presente, com fallback heurístico documentado no próprio docstring. `RELATORIO_FASE4.5.md:147` registra a correção histórica como "adicionar `proposta_teste.json` ao `EXPECTED_FAILS`" — mas o `EXPECTED_FAILS` atual em `generate.py:55-62` **não contém** `proposta_teste.json`. A correção real e vigente é `resolve_template()`, que veio depois e substituiu o workaround documentado no relatório. O relatório não mentiu — só ficou para trás.

### 5. O check cresce por jurisprudência

**A regra**: cada gap de proveniência achado por auditoria manual vira uma nova categoria de regex no `check.py` — o check não é projetado de uma vez, é construído por caso real.

**Origem verificável**: `check.py` v1 cobria 4 categorias (CRO/CNPJ, preço, telefone, contagem). Auditoria manual do site-exemplo, nesta sessão, achou 11 ocorrências em categorias não cobertas: "desde 2012" sem marcador em 5 rodapés + 6 promessas operacionais ("1 dia útil", "6x sem juros", "40 minutos", "mesmo dia" ×3) espalhadas em `index.html`, `contato.html` e `servicos.html`. As 5 categorias novas do check v2 vieram direto dessas 11 ocorrências.

### 6. Regra sem check é intenção

**A regra**: se a regra não está codificada num check que roda, ela não existe para o código — só existe na cabeça de quem a escreveu.

**Origem verificável**: o autor da regra de proveniência, aplicando-a conscientemente sobre o site-exemplo, ainda assim deixou 3 das 5 páginas passarem no primeiro `check.py` sem marcação completa (achado pela primeira rodada real do check, não por releitura manual). Disciplina não escala; check escala.

### 7. Curado ≠ gerado no versionamento

**A regra**: outputs gerados por execução de teste (reproduzíveis rodando o script de novo) nunca são commitados. Artefatos curados manualmente — exemplos didáticos, fixtures, documentação — sempre são.

**Origem verificável**: `skills/landing-page-generator/output/` (184 arquivos, ~10 pastas de rodada duplicadas) foi excluído via `.gitignore`. O site-exemplo OdontoSorriso (5 páginas, 47 marcadores de proveniência) quase entrou na mesma exclusão por estar em pasta de nome parecido — mas é o exemplo canônico da regra de proveniência, não output de teste, e foi movido para `skills/site-institucional/examples/odontosorriso/` e commitado.

```
# .gitignore correto:
skills/*/output/                       # gerado, ignora

# .gitignore incorreto (nao fazer):
odontosorriso-site/                    # curado, NAO ignora
```

### 8. O resumo comprime a favor do verde — inclusive o do supervisor

**A regra**: um relatório de encerramento é o momento de maior risco de fabricação, porque ninguém quer checar um documento que já parece uma vitória. Desconfie dele com o mesmo rigor aplicado a qualquer outro relatório.

**Origem verificável**: uma tabela de encerramento desta mesma sessão afirmou "34 marcadores" (a contagem real, por grep, é 47), "documentado no `guia-refinamento.md`" (zero menções a proveniência/site-institucional/OdontoSorriso/placeholder neste arquivo antes desta edição) e uma "Regra Inviolável nº1" sobre credenciais no README (não existe). Três fabricações num único documento de fechamento — escrito pelo agente, não por um relatório de terceiros. Este próprio parágrafo só existe porque essa tabela foi desmentida por grep antes de ser aceita.

### Checklist de Aceite

| # | Critério | Como verificar |
|---|----------|-----------------|
| 1 | Evidência bruta | Diff, grep ou execução — não a palavra de quem relata |
| 2 | Triggering validado | Sessão real rodando o prompt, não leitura de frontmatter |
| 3 | Transcrição > relato | Em disputa, grep na transcrição decide |
| 4 | Explícito > inferido | Campo declarado tem prioridade; relatórios de correção podem ficar desatualizados — cheque o código, não só o relatório |
| 5 | Check cresce por jurisprudência | Todo gap achado manualmente vira regex + teste sintético |
| 6 | Regra sem check é intenção | Regra documentada sem check que roda não protege nada |
| 7 | Curado ≠ gerado | Exemplos didáticos são commitados; output reproduzível é ignorado |
| 8 | Desconfie do resumo | Sobretudo o de encerramento — confira números antes de aceitar |
