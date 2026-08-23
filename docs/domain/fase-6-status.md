# Status da Fase 6 — Camada de IA

## O que está pronto e validado

- **Payload estruturado** (`application/explanations/payload.py`): extrai só os campos numéricos já calculados pelo motor, arredondados para centavos — nunca deriva nada novo.
- **Saída estruturada** (`application/explanations/schemas.py`): `ExplanationOutput` só tem campos de texto (title, body, warnings) — impossível a IA "retornar" um número que vire fonte de verdade, porque o schema não tem onde colocar um.
- **Guardrails** (`infra/ai/guardrails.py`): bloqueia pergunta de recomendação individualizada (`"devo vender?"`, `"vale a pena?"`) antes mesmo de montar o prompt — testado com 7 casos, positivos e negativos.
- **Validador numérico** (`infra/ai/numeric_validator.py`): extrai todo valor `R$ X.XXX,XX` do texto gerado e descarta a resposta inteira se algum não bater com o payload (tolerância de R$ 0,02). Testado inclusive com número "alucinado" que não existe em lugar nenhum do payload.
- **RAG restrita** (`infra/ai/rag.py` + `docs/domain/rag-corpus/`): recuperação léxica (contagem de termos compartilhados), não embeddings — corpus pequeno (5 documentos curados: marcação a mercado, IR regressivo, IOF regressivo, custódia B3, metodologia de precificação) não precisa de vetor para ter recall razoável, e evita depender de uma API de embeddings antes mesmo de ter a chave do LLM principal configurada. `pgvector` só entra se o corpus crescer a ponto de precisão léxica não bastar.
- **Fallback estático** (`application/explanations/templates.py`): template determinístico, mesma voz/formato da explicação por IA, nunca toca rede.
- **Orquestração** (`application/explanations/service.py`): guardrail → payload → RAG (se houver pergunta) → LLM → validação numérica → fallback em qualquer falha ou divergência. A IA nunca é dependência crítica — testado inclusive com JSON malformado, campo faltando no schema, e provedor indisponível.
- **`POST /api/v1/explanations`** funcionando de ponta a ponta contra o backend real — testado sem `GEMINI_API_KEY` configurada (cai no fallback com os números exatos da simulação, curl confirmado) e com um `FakeLlmClient` via override de dependência (mesmo padrão de `BondCatalogPort`/`SimulationStore`).
- **178 testes passando**, mypy `--strict` limpo em 69 arquivos.

## Decisões tomadas nesta fase

- **Provedor: Gemini 1.5 Flash** (`infra/ai/gemini_client.py`), escrito contra a API real do SDK `google-genai` (verificada nesta sessão: `genai.Client(...).models.generate_content(...)`, `GenerateContentConfig` com `system_instruction` e `response_json_schema`) — mas **nunca chamado com uma chave de verdade**. Estruturalmente correto, não validado ao vivo, mesma ressalva transparente já usada para Postgres antes da Fase 4/5.3. Se o Google já tiver descontinuado `gemini-1.5-flash` na hora de testar com a chave real, o erro sobe como exceção normal e cai no fallback — não silencia, mas o modelo precisa ser atualizado depois de confirmar qual Flash está disponível.
- **`UnavailableLlmClient`**: quando `GEMINI_API_KEY` não está configurada, a API nunca falha por causa disso — devolve um cliente que levanta erro só na hora de gerar (não na hora de montar), pra o mesmo caminho de fallback do orquestrador cuidar disso sem tratamento especial na rota.
- **Function calling explicitamente adiado**: perguntas contrafactuais tipo "e se eu vender em março?" deveriam virar uma chamada tipada de volta ao motor (`§21` do prompt original), mas isso só é possível de testar de verdade observando o comportamento real do modelo decidindo quando chamar a ferramenta — não dá pra validar isso com um fake sem inventar o comportamento do Gemini. Fica para quando houver a chave.
- **Corpus da RAG começou pequeno de propósito** (sua escolha) — 5 documentos, todos já validados com citação de fonte em sessões anteriores (não é conteúdo novo inventado para a RAG). Crescer o corpus é trabalho de conteúdo, não de código — a `LexicalRetriever` não muda.

## Pendências explícitas

- Testar `GeminiClient` contra a API de verdade assim que houver `GEMINI_API_KEY` — inclusive confirmar se `gemini-1.5-flash` ainda existe ou precisa virar `gemini-2.0-flash`/mais recente.
- Function calling (perguntas contrafactuais → `simulate_sale`/`simulate_scenario` tipados).
- Expandir o corpus da RAG além dos 5 documentos iniciais, se o produto passar a receber perguntas fora desse escopo.
- `pgvector` — só se a recuperação léxica se mostrar insuficiente com um corpus maior.
