# ADR-003 — A IA nunca calcula números

## Status
Aceito. Não negociável dentro do escopo deste produto.

## Contexto
VÉRTICE explica marcação a mercado de renda fixa. Um número financeiro errado apresentado com a confiança de um texto fluente é pior do que nenhuma explicação — mina a credibilidade do produto inteiro, não só da resposta pontual.

## Decisão
A camada de IA recebe um payload já calculado pelo motor determinístico e produz apenas campos textuais (structured output validado por Pydantic). Perguntas contrafactuais viram chamadas tipadas de volta ao motor (function calling), nunca estimativa da LLM. Toda resposta passa por um validador que extrai números do texto gerado e a descarta se divergir do payload de origem. Se qualquer etapa falhar, o sistema cai em template estático — a IA é aditiva, nunca uma dependência crítica do caminho que mostra números ao usuário.

## Alternativas descartadas
- **Deixar a LLM calcular diretamente com a pergunta em linguagem natural** — mais simples de implementar, mas transforma o produto num gerador de números plausíveis-porém-não-confiáveis, o oposto do que o produto promete (confiança, precisão).
- **Confiar nos números da LLM e só validar "parece razoável"** — sanity check heurístico não é o mesmo que correto; a decisão foi comparação exata contra o payload, não plausibilidade.

## Consequências
Todo novo tipo de pergunta que o produto queira responder via IA precisa primeiro existir como função tipada no motor. Isso é fricção deliberada: se a pergunta não tem uma função determinística por trás, o produto não deveria estar respondendo com um número de qualquer forma.
