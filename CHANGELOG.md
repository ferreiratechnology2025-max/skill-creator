# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

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
