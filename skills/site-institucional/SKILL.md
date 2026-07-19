---
name: site-institucional
description: |
  Cria site institucional multi-página (tipicamente 5: Início, Sobre,
  Serviços/Produtos, Equipe, Contato) para um negócio local, com identidade
  visual própria por briefing. Use quando o pedido for "site institucional",
  "site de N páginas", "site para minha clínica/loja/escritório", ou pedir
  explicitamente múltiplas páginas navegáveis (não uma página única).
  NÃO use para landing page, página de vendas ou página de captura de uma
  página só — isso é landing-page-generator.
---

# site-institucional

Gera um site institucional multi-página com HTML/CSS/JS estático, sem
dependências externas além de fontes web. Cada claim factual específico
(telefone, endereço, CRO/CNPJ, preço, contagem de clientes, nome de equipe)
carrega uma proveniência declarada — `busca`, `usuário` ou `placeholder` —
nunca aparece formatado como fato verificado sem ser um.

## Gatilhos

- "site institucional [de N páginas]"
- "site para minha clínica/loja/escritório/consultório"
- "página institucional", "site com Sobre, Serviços, Contato"
- Pedido explícito de múltiplas páginas navegáveis para um negócio
- NÃO aciona: "landing page", "página de vendas", "página de captura" (ver
  `landing-page-generator`) nem "post de Instagram"/"artigo de blog"

## Pré-requisitos

- Nome do negócio e setor (mínimo para começar)
- Nenhuma dependência de build — HTML/CSS/JS puro
- Fontes web (Google Fonts ou equivalente) via `<link>`, sem instalação

## Workflow

1. **Nomear** o negócio, o setor, e as N páginas (padrão: Início, Sobre,
   Serviços, Equipe, Contato — ajustar ao setor).
2. **Perguntar por dados reais** antes de escrever qualquer claim
   específico: telefone, endereço, CRO/CNPJ, preços, nomes de equipe,
   contagens (clientes/anos/avaliações). Se o usuário fornecer no pedido
   ou anexar dados estruturados, usar com `fonte: usuário`. Se autorizado
   a pesquisar, usar com `fonte: busca` e registrar o que foi buscado.
3. **Definir o token system de design** (cor, tipografia, layout, elemento
   assinatura) ancorado no vocabulário do setor — carregar a skill
   `frontend-design` nesta etapa. Nunca usar paleta/layout genérico padrão.
4. Escrever `css/style.css` e `js/script.js` compartilhados (nav mobile,
   link ativo, validação de formulário client-side).
5. Escrever cada página HTML reaproveitando header/footer.
6. **Para todo claim sem `fonte: busca` ou `fonte: usuário`**: marcar com
   comentário HTML imediatamente acima do bloco:
   `<!-- PLACEHOLDER fonte: nenhuma — <claim> é fictício, substituir por dado real -->`
7. Rodar `scripts/check.py` em cada página gerada (ver Regras Invioláveis).
8. **Reportar ao usuário**, em texto, a lista de claims marcados como
   placeholder — não deixar só no comentário HTML invisível.

## Exemplos

**Input:** "cria um site institucional de 5 páginas para a clínica
OdontoSorriso" (sem dados adicionais fornecidos)

**Output:** 5 páginas HTML + CSS/JS compartilhados, identidade visual
própria ao setor odontológico, com todo telefone/endereço/CRO/preço/nome de
equipe/contagem de pacientes gerado como placeholder plausível e marcado
com comentário `<!-- PLACEHOLDER fonte: nenhuma -->` acima de cada bloco,
mais um resumo em texto ao usuário listando os campos fictícios a
substituir antes de publicar.

**Input:** "cria um site institucional de 4 páginas para a Padaria Trigo
Dourado — telefone (62) 3333-1000, endereço Rua das Flores 90, Goiânia,
fundada em 2008"

**Output:** 4 páginas usando telefone/endereço/ano fornecidos com
`fonte: usuário` (sem comentário placeholder nesses campos — vieram do
usuário); demais claims não fornecidos (ex. nomes de padeiros, preços)
seguem como placeholder marcado.

## Edge Cases

1. **Usuário fornece dados completos no próprio pedido.** Não gerar
   placeholder para o que já foi dado — usar direto com `fonte: usuário`.
   Gerar placeholder apenas para o que realmente falta.
2. **Pedido ambíguo entre site institucional e landing page** (ex. "página
   para minha clínica"). Perguntar: página única com um objetivo de
   conversão (→ landing-page-generator) ou site multi-página institucional
   (→ esta skill)? Não assumir.
3. **Setor sem vocabulário visual óbvio** (ex. "consultoria financeira").
   Ainda assim evitar o default genérico (cream+serifa ou dark+neon) —
   ancorar no que é específico do setor (documentos, gráficos, confiança
   numérica) em vez de decoração arbitrária.
4. **Usuário pede para publicar/enviar o site com placeholders ainda
   presentes.** Avisar explicitamente antes de considerar a entrega
   concluída — placeholder visível só no comentário HTML não é aviso
   suficiente ao usuário final.

## Regras Invioláveis

- NUNCA formatar um dado inventado (CRO, CNPJ, telefone, endereço, preço,
  contagem de clientes/anos) de forma indistinguível de um dado
  verificado — todo claim tem `fonte: busca | usuário | placeholder`
  declarada em comentário HTML acima do bloco.
- NUNCA inventar credenciais, tokens ou chaves nos arquivos gerados.
- SEMPRE rodar `scripts/check.py` em cada página antes de entregar.
- SEMPRE reportar em texto ao usuário quais claims ficaram como
  placeholder — o comentário HTML não substitui o aviso.
- SEMPRE carregar a skill `frontend-design` antes de definir o token
  system — nunca reaproveitar cegamente a paleta de um projeto anterior.
