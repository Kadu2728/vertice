# Status da Fase 7 — SEO e Performance

## O que está pronto e validado

- **Páginas indexáveis por título real** (`frontend/app/[slug]/page.tsx`) — uma URL por série de título, seguindo a nomenclatura oficial do Tesouro Direto (`/tesouro-prefixado-2029`, `/tesouro-selic-2027`, `/tesouro-ipca-2035`, `/tesouro-ipca-juros-semestrais-2035`, `/tesouro-prefixado-juros-semestrais-2029`), gerada a partir do catálogo real da API — nenhuma página fabricada sem título correspondente de fato existente no banco.
- **Conteúdo real, não wrapper vazio**: cada página mostra a taxa indicativa atual (buscada de `GET /bonds/{id}/quotes`, dado real), uma explicação do tipo de título, e — para LTN/NTN-F, os dois tipos que a API já suporta — o simulador embutido e pré-selecionado nesse título. Para NTN-B/NTN-B Principal/LFT, mostra o conteúdo informativo real mas é honesto que a simulação ainda não está disponível, em vez de embutir um simulador quebrado.
- **Metadata completa por página**: title (via template `%s — VÉRTICE`), description, canonical, Open Graph (title/description/type) — verificado direto no `<head>` renderizado, não só no código.
- **`sitemap.xml` e `robots.xml`** via convenção de arquivo do Next.js, gerados a partir do catálogo real — testado que lista todas as séries reais do banco.
- **404 real** (`notFound()`) para slug que não corresponde a nenhum título — testado que devolve HTTP 404 de verdade, não uma página de erro com status 200.
- **Performance**: `/[slug]` é renderizada sob demanda (SSR, não SSG) com cache de `fetch` do Next.js (`revalidate: 3600`) nas chamadas à API — decisão consciente, ver abaixo.

## Decisões tomadas nesta fase

- **SSR sob demanda, não SSG (`generateStaticParams` não foi usado)**: gerar estático no build exigiria o backend acessível na hora do `next build` — um acoplamento que não existe entre o deploy do frontend (Vercel) e do backend (Render), que são pipelines separados. SSR entrega o mesmo HTML já renderizado para o crawler, só que na hora da requisição em vez de antecipado no build; a diferença não afeta indexabilidade, só o momento em que o trabalho acontece.
- **Cache via `fetch` do Next.js (`next: { revalidate: 3600 }`), não Redis**: o discovery original (§33) planejava Redis para cache de simulações; isso não foi implementado nesta fase porque exigiria subir mais um serviço local (mesmo caminho do Postgres via winget) para um ganho que o cache nativo do Next já cobre para o caso de uso desta fase (catálogo e cotações, que mudam no máximo uma vez por dia). Redis para cache de resultado de simulação (o caso de uso original do §33) continua pendente — não foi descartado, só não é o gargalo desta fase.
- **Slugs seguem a nomenclatura do Tesouro Direto** (`tesouro-prefixado`, `tesouro-ipca`, `tesouro-selic`), não a sigla ANBIMA (LTN/NTN-B/LFT) — é o que uma pessoa digita no Google, não o código técnico do título.

## Pendências explícitas

- Cache Redis de resultado de simulação (§33 do discovery) — não é mais bloqueador de nada, mas segue no roadmap.
- Imagem de Open Graph dinâmica por título (preview social visual, não só texto) — não implementada nesta fase por tempo; os metadados de texto (title/description) já funcionam para preview em redes sociais mesmo sem imagem customizada.
- Dado estruturado (schema.org) — avaliado e não incluído: o tipo mais próximo (`FinancialProduct`) não representa com precisão um título público brasileiro sem forçar campos que não existem nos dados reais; melhor não incluir do que incluir dado estruturado impreciso.
