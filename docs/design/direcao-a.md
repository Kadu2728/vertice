# Direção A — Papel de Ofício, selo dourado

Fase 5.0 aprovada, Fase 5.1 (tokens + primitivos) implementada. Fonte visual: [artifact de direções](../..) apresentado e revisado nesta fase — ver histórico da conversa para as três direções originais e a autocrítica de cada uma.

## Conceito

Um título público nasce como um papel emitido pelo Tesouro — um registro formal. A interface trata cada simulação como um lançamento de livro-razão: preto profundo como a tinta do lançamento, dourado como o selo de chancela do que foi calculado.

**Sobre a referência à XP Inc.**: o usuário pediu para incorporar a combinação preto+dourado, a família de cor mais reconhecível da XP. Não foi replicado nenhum elemento de marca da XP — sem logotipo, wordmark, ou qualquer coisa que faça o VÉRTICE parecer produto ou afiliado da XP. O que foi trazido é a família de cor, reencaixada no conceito que a Direção A já tinha (papel oficial → selo dourado), não um empréstimo estético sem relação com o conteúdo.

## Paleta

| Token | Hex | Papel |
|---|---|---|
| `--background` (tinta) | `#0B0A08` | Fundo dominante — preto quente, não neutro de tela |
| `--foreground` (papel) | `#F2ECDD` | Texto principal — o "papel" sobrevive como a cor do texto sobre a tinta |
| `--card` | `#14120C` | Superfícies elevadas (lançamentos, formulários) |
| `--primary` (selo) | `#D4A72C` | Usado só em três lugares com função: valor principal, selo de chancela, hairlines de destaque — nunca fundo, nunca espalhado |
| `--accent` (selo abatido) | `#8C6E22` | Selo em estado secundário/hover |
| `--muted-foreground` | `#A79C7C` | Texto secundário, rótulos |
| `--destructive` / `--negative` (lacre) | `#B14A3A` | Deduções, tributo, valores negativos |
| `--positive` (verdete) | `#7FA491` | Ganho, impacto positivo |
| `--border` | `#2E2A1C` | Hairlines |
| `--ring` | `#D4A72C` | Foco de teclado — dourado, visível sobre o fundo escuro |

`--positive`/`--negative` são tokens semânticos deliberadamente separados de `--primary` — direção de valor financeiro não é o acento decorativo do produto (ver `artifact-design` skill: "Semantic color is separate from the accent hue and doesn't count as your accent").

Mundo único, deliberadamente escuro — **não há alternância claro/escuro**. A Direção A é um compromisso visual fechado, não um tema adaptável; não implementar toggle de tema a menos que pedido.

## Tipografia

- **Display** — Fraunces (500/600), uso restrito a headings (`font-heading`). Evoca a autoridade de uma lauda oficial.
- **Texto** — Source Sans 3 (400/500/600), corpo e UI.
- **Dado** — IBM Plex Mono (400/500/600), `font-mono` + classe utilitária `.tabular` (`font-variant-numeric: tabular-nums`) em todo número financeiro, para casas decimais alinharem em coluna.

Carregadas via `next/font/google` em `app/layout.tsx` — self-hosted pelo Next, não fazem requisição a fonts.googleapis.com em runtime.

**Armadilha encontrada**: variáveis de fonte do `next/font` ficam definidas no `<body>` (onde o Next injeta a className), não no `<html>`. Uma regra `html { font-sans }` não enxerga essas variáveis porque CSS custom properties não sobem de filho para pai — o fallback silencioso caiu para Times New Roman até a correção (`font-sans` aplicado direto no `body`). Verificado via computed styles no navegador, não por inspeção visual.

## Raio e densidade

`--radius: 0.125rem` (2px) — propositalmente afiado, não o `rounded-lg` padrão do shadcn (ver §28.2 do prompt: "rounded-lg everywhere" é um dos padrões proibidos). Todos os componentes shadcn herdam isso automaticamente via `--radius-sm/md/lg/xl` derivados no `@theme`, sem editar componente a componente.

## Onde está

- `frontend/app/globals.css` — todos os tokens.
- `frontend/app/layout.tsx` — carregamento das três fontes.
- `frontend/components/ui/*` — primitivos shadcn (Base: Radix UI; preset inicial Nova, integralmente sobrescrito pelos tokens acima) — button, input, label, select, slider, separator, card, badge.
- `frontend/app/design-tokens/page.tsx` — página de verificação visual (paleta, tipografia, formulário de simulação, cenário, lançamento de resultado montados com os primitivos reais).

## Validado

`npm run build` limpo (tipos, lint, build de produção). Estilos computados verificados via JS no navegador real (background, texto, fontes, cor/raio de botão, cores semânticas, superfície de card) — batem exatamente com a paleta acima. Não foi possível tirar screenshot nesta sessão (painel do navegador não exibido do lado do usuário); a verificação foi por inspeção de `getComputedStyle`, não visual.
