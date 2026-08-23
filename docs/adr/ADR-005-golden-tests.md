# ADR-005 — Estratégia de golden tests

## Status
Aceito.

## Contexto
Testes unitários provam que uma fórmula faz o que o código diz que ela faz. Eles não provam que a fórmula está certa em relação ao mercado real. Para um motor de precificação, essa segunda prova é a que importa para o usuário.

## Decisão
Golden tests recalculam o PU (e, onde aplicável, o valor líquido) para uma amostra ampla de `(título, data)` reais e comparam contra o preço oficial publicado pelo Tesouro Transparente/ANBIMA, com tolerância definida por tipo de título (R$ 0,01 onde a metodologia oficial suporta essa granularidade sem ambiguidade — ver ADR-004). Fixtures congeladas e versionadas no repositório, não buscadas ao vivo durante o teste. Rodam no CI em todo PR que toca `domain/`, com gate bloqueante: divergência de precisão financeira quebra o build, não gera warning.

## Alternativas descartadas
- **Só testes unitários com valores calculados à mão** — prova a fórmula internamente consistente, mas não pega erro sistemático de metodologia (ex.: convenção de calendário errada que desloca todo o cálculo de forma uniforme e "parece" certo).
- **Comparação aproximada com tolerância larga genérica (ex.: 1%)** — esconderia exatamente o tipo de erro de centavo/arredondamento que mais importa detectar cedo; tolerância larga é abdicar do propósito do teste.
- **Rodar golden tests só manualmente antes de release** — divergência introduzida por um PR ficaria invisível até o release seguinte, quando já é mais caro rastrear a causa.

## Consequências
Manter os fixtures atualizados e ampliá-los conforme novos tipos de título/cenário são suportados é trabalho contínuo, não uma tarefa de uma vez só — cada bug de precisão encontrado em produção deveria virar um novo caso golden, não só um patch silencioso.
