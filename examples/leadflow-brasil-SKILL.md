---
name: leadflow-brasil
description: Sistema agentic de geração e outreach de leads B2B no Brasil. Pesquisa empresas via Google Maps, enriquece contatos, qualifica com scoring, gera mensagens personalizadas e envia e-mails com retry e backoff. Meta: 30+ leads qualificados/dia.
---

# skill-leadflow-brasil

## Descrição
Sistema agentic de geração e outreach de leads B2B no Brasil. 
Pesquisa empresas via Google Maps, enriquece contatos (e-mail, LinkedIn), 
qualifica com scoring inteligente, gera mensagens hiper-personalizadas via IA 
e realiza envio controlado de e-mails com retry e backoff exponencial.

## Gatilhos
Ative quando o usuário pedir:
- "Gerar leads para [segmento] em [cidade]"
- "Buscar empresas de [segmento] em [cidade]"
- "Executar workflow de [busca/enriquecimento/qualificação/outreach]"
- "Enviar e-mails para leads qualificados"
- "Gerar relatório de performance de leads"
- "Otimizar mensagens de outreach"
- "LeadFlow [comando]"

## Pré-requisitos
- Python 3.10+ instalado
- Variáveis de ambiente configuradas em `.env`:
  - `GOOGLE_MAPS_API_KEY` — para busca de empresas
  - `HUNTER_API_KEY` ou `SNOV_API_KEY` — para enriquecimento de e-mails
  - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` — ou Resend API key
  - `FROM_EMAIL` — remetente dos e-mails
- Dependências Python: `pandas`, `requests`, `tenacity`, `python-dotenv`
- Pastas `data/` criadas:
  - `data/raw_leads.csv`
  - `data/enriched_leads.csv`
  - `data/qualified_leads.csv`

## Multi-Plataforma
Esta skill funciona em:
- **Claude Code**: `~/.claude/skills/leadflow-brasil/`
- **Codex**: `~/.codex/skills/leadflow-brasil/`
- **OpenCode**: `~/.config/opencode/skills/leadflow-brasil/`

Scripts Python em `tools/` são executados via shell do agente.

## Workflow

### Pipeline Completo
1. **Planejamento**: Entender segmento, cidade, critérios de qualificação e tom de mensagem
2. **Busca**: Executar `scraper_maps.py` → buscar empresas no Google Maps → salvar em `data/raw_leads.csv`
3. **Enriquecimento**: Executar `enricher.py` → encontrar e-mails e LinkedIn via Hunter.io/Snov.io → salvar em `data/enriched_leads.csv`
4. **Qualificação**: Executar `qualifier.py` → aplicar scoring (tamanho, presença web, tecnologias) → salvar em `data/qualified_leads.csv`
5. **Geração de Mensagem**: Executar `message_generator.py` → gerar mensagens hiper-personalizadas via IA para cada lead qualificado
6. **Outreach**: Executar `sender.py` → enviar e-mails com retry e backoff exponencial → registrar métricas
7. **Feedback**: Analisar respostas, taxas de abertura/clique e sugerir otimizações para próximo ciclo

### Comandos Rápidos
- `/leadflow buscar [segmento] em [cidade]` → Executa workflow 01-03 (busca + enriquecimento + qualificação)
- `/leadflow qualificar` → Executa workflow 03 em leads já enriquecidos
- `/leadflow mensagens` → Executa workflow 04 para leads qualificados
- `/leadflow enviar --limite 20` → Executa workflow 05 com limite de envios
- `/leadflow relatorio` → Gera métricas de performance do pipeline
- `/leadflow otimizar` → Analisa feedback e sugere melhorias no tom, timing ou segmentação

## Exemplos

### Exemplo 1: Busca completa
**Input:**
```
/leadflow buscar agências de marketing em São Paulo
```
**Output esperado:**
```
✅ 47 leads encontrados no Google Maps
✅ 38 e-mails enriquecidos via Hunter.io (taxa: 80%)
✅ 22 leads qualificados (score médio: 74)
📁 Arquivos salvos em data/
   - raw_leads.csv (47 registros)
   - enriched_leads.csv (38 registros)
   - qualified_leads.csv (22 registros)
```

### Exemplo 2: Envio de outreach
**Input:**
```
/leadflow enviar --limite 20 --personalizado
```
**Output esperado:**
```
✅ 20 e-mails enviados
📊 Taxa de entrega: 95% (19/20)
📊 Taxa de abertura estimada: 25%
📝 Retry automático configurado para 5 falhas
⏱️ Backoff: 2s, 4s, 8s, 16s, 32s
📁 Log salvo em data/outreach_log_2026-06-01.csv
```

### Exemplo 3: Relatório de performance
**Input:**
```
/leadflow relatorio --semana-atual
```
**Output esperado:**
```
📈 Performance LeadFlow — Semana 23/2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Leads gerados:        156
Enriquecimento:       128 (82%)
Qualificados:         89 (score > 70)
E-mails enviados:     85
Taxa de entrega:      94%
Taxa de resposta:     8% (7 respostas)
Lead mais promissor:  Agência XYZ (score 92, respondeu em 2h)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Sugestão: Aumentar limite diário para 35 leads (capacidade atual subutilizada)
```

## Edge Cases

- **API do Google Maps indisponível**: Aguardar 60s e retry (máximo 3 tentativas). Se persistir, pausar pipeline e alertar usuário com timestamp.
- **E-mail não encontrado para lead**: Marcar como "enriquecimento parcial", não descartar. Tentar alternativa (Snov.io se Hunter falhou, ou busca manual no site).
- **Taxa de bounce > 10%**: Pausar envios imediatamente, alertar usuário para verificar qualidade da lista. Sugerir re-validação de e-mails.
- **Limite diário de API atingido**: Registrar no log, salvar estado atual, continuar automaticamente no dia seguinte.
- **Lead já contactado nos últimos 30 dias**: Pular automaticamente. Registrar no log para evitar duplicidade.
- **Resposta negativa do lead**: Registrar sentimento (negativo), adicionar à blacklist por 90 dias, não contactar novamente neste período.
- **Mensagem personalizada falha (IA indisponível)**: Usar template de fallback genérico mas profissional, marcar para revisão manual.
- **SMTP bloqueado / Resend indisponível**: Tentar canal alternativo se configurado. Se não, pausar e alertar.
- **LGPD — pedido de remoção**: Processar imediatamente, remover de todas as listas, confirmar remoção em 72h, registrar para compliance.

## Guardrails (Regras Invioláveis)

1. **Respeito total à LGPD**: Todo lead deve ter base legal de contato. Incluir opção de descadastro em todos os e-mails. Processar remoções em até 72h.
2. **Máximo 2 contatos por lead**: Primeiro e-mail + 1 follow-up. Nunca spammar.
3. **Todos os envios são registrados**: Log completo em `data/outreach_log_YYYY-MM-DD.csv` com timestamp, destinatário, status, mensagem_id.
4. **Retry com backoff exponencial**: 2s → 4s → 8s → 16s → 32s. Máximo 5 tentativas.
5. **Nunca expor credenciais**: Todas as chaves API e senhas em `.env`. Nunca em logs, mensagens ou SKILL.md.
6. **Validação de e-mails antes do envio**: Verificar formato (regex) + verificação de domínio (MX record). Não enviar para e-mails inválidos.
7. **Aquecimento de conta de e-mail**: Se conta nova, limitar a 10 e-mails/dia nas primeiras 2 semanas, aumentando gradualmente.

## Métricas de Sucesso

| Métrica | Meta | Frequência |
|---------|------|------------|
| Leads gerados por dia | 30+ | Diária |
| Taxa de enriquecimento (e-mails encontrados) | > 70% | Diária |
| Score médio dos leads | > 65 | Semanal |
| Taxa de entrega de e-mails | > 90% | Diária |
| Taxa de resposta | Monitorar e otimizar | Semanal |
| Taxa de bounce | < 5% | Diária |
| Leads qualificados / Leads gerados | > 50% | Semanal |

## Refinamento Pós-Deploy

1. **Testar com segmento real**: Escolher 1 segmento (ex: "agências de marketing em São Paulo") e executar pipeline completo
2. **Identificar gargalos**: Qual etapa tem menor taxa de sucesso? (busca, enriquecimento, qualificação, mensagem, envio?)
3. **Ajustar scoring**: Revisar pesos do qualifier.py baseado em conversões reais
4. **Refinar mensagens**: Analisar respostas positivas vs negativas, ajustar tom e CTA
5. **Atualizar evals.json**: Adicionar casos de teste baseados em falhas reais encontradas
6. **Versionar**: Adicionar changelog no SKILL.md

## Changelog

### 2026-06-01 — v1.0
- Deploy inicial com 6 workflows completos
- Integração Google Maps + Hunter.io + SMTP/Resend
- Scoring inicial: tamanho empresa, presença web, tecnologias

---

**Desenvolvido com Agentic Workflows** | Transição de Construtor → Arquiteto
