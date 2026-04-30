# Roadmap — Travel Agent IA

Este documento detalha o que vem a seguir no projeto, organizado em fases. Cada item tem rationale, critério de aceitação e tamanho estimado de esforço.

## Status atual (v0.1)

O que já funciona:

- Grafo LangGraph com 7 agentes (Manager, Weather, Tourism, Transport, Accomodation, Budget, Conversational)
- Integração com OpenWeatherMap, TripAdvisor e Booking.com via RapidAPI
- LLM local via Ollama (qwen2.5:7b)
- Frontend Next.js com chat persistido por usuário
- Auth via Supabase com RLS no banco
- Tracing com Langfuse

## Fase 1 — robustez do core

Foco: deixar a base atual mais sólida antes de adicionar funcionalidades novas.

### 1.1 Tool-use mais robusto

**Por quê.** Hoje cada agente tem suas tools fixas em código. Quero permitir que tools sejam descobertas/registradas dinamicamente, e que o agente decida em tempo de execução qual chamar (em vez do roteamento ser parcialmente hardcoded no grafo).

**Critério de aceitação.**
- Adicionar uma nova tool requer apenas criar o arquivo em `backend/src/tools/` e ela ser descoberta automaticamente.
- O agente é capaz de chamar zero ou várias tools por turno.

**Esforço.** ~1 fim de semana.

### 1.2 Memória persistente entre sessões

**Por quê.** Hoje cada conversa começa do zero. Idealmente o sistema deveria lembrar preferências do usuário (estilo de viagem, restrições alimentares, orçamento típico) entre sessões.

**Critério de aceitação.**
- Tabela `user_memory` no Supabase com embeddings (pgvector).
- ManagerAgent enriquece os parâmetros com memórias relevantes recuperadas.
- Memórias são extraídas e gravadas implicitamente após cada sessão.

**Esforço.** ~2 fins de semana.

### 1.3 Avaliação dos agentes

**Por quê.** Hoje a única forma de saber se um agente está performando bem é testando à mão. Quero um harness de avaliação que rode em CI.

**Critério de aceitação.**
- Conjunto de ~20 prompts de teste com saídas esperadas (ground truth).
- Métricas por agente: trajectory match, tool-use accuracy, factual correctness.
- Aplicação dos padrões do curso *Evaluating AI Agents* da DeepLearning.AI.
- Relatório de avaliação versus baseline rodando em GitHub Actions.

**Esforço.** ~2-3 fins de semana.

## Fase 2 — experiência do usuário

### 2.1 UI com indicação visual das tool calls

**Por quê.** O usuário hoje vê apenas a resposta final. Mostrar em tempo real quais agentes estão rodando e quais tools estão sendo chamadas aumenta a confiança e dá pistas quando algo dá errado.

**Critério de aceitação.**
- Streaming de eventos do backend para o frontend (SSE).
- Frontend renderiza chips/cards mostrando "WeatherAgent → get_forecast()", "TourismAgent → get_attractions()" etc., conforme acontecem.
- Estados visuais: pending, in-progress, complete, error.

**Esforço.** ~1-2 fins de semana.

### 2.2 Múltiplos provedores de LLM

**Por quê.** Ollama é ótimo em dev, mas em produção a qualidade do tool-calling com modelos menores é o gargalo. Permitir trocar para OpenAI ou Anthropic via flag de configuração.

**Critério de aceitação.**
- Abstração de provedor em `backend/src/agents/llm_provider.py`.
- Variável `LLM_PROVIDER=ollama|openai|anthropic` controla o backend.
- README documenta o trade-off e as chaves necessárias.

**Esforço.** ~1 fim de semana.

### 2.3 Idiomas

**Por quê.** Hoje o sistema é PT-only por causa dos prompts. Suportar EN abriria pra um público bem maior.

**Critério de aceitação.**
- Detecção automática do idioma do input.
- System prompts em PT e EN.
- Resposta no mesmo idioma da pergunta.

**Esforço.** ~3-4 dias.

## Fase 3 — produção

### 3.1 Testes de integração

**Por quê.** Os testes atuais são unitários. Falta um teste que exercite o grafo inteiro com LLM mockado e verifique o fluxo de ponta a ponta.

**Critério de aceitação.**
- Suite de testes de integração que mocka apenas as APIs externas (Weather, RapidAPI) e usa um LLM real (rodando localmente em CI ou mock determinístico).
- Cobertura mínima de 70% nos módulos `agents/`, `graph/`, `api/`.

**Esforço.** ~1-2 fins de semana.

### 3.2 Deploy público

**Por quê.** Tornar o projeto acessível sem precisar clonar e rodar localmente.

**Critério de aceitação.**
- Frontend em Vercel ou Cloudflare Pages.
- Backend em Fly.io, Railway ou Azure Container Apps.
- LLM hospedado em provedor (OpenAI/Anthropic) — Ollama não escala em deploy gratuito.
- Domínio próprio e HTTPS.

**Esforço.** ~1 fim de semana (depois de 2.2 estar pronto).

### 3.3 Rate limiting + custo

**Por quê.** Em deploy público com LLM pago, é essencial limitar uso por usuário pra controlar gasto.

**Critério de aceitação.**
- Rate limiting via `slowapi` no FastAPI.
- Tracking de tokens consumidos por usuário no Supabase.
- Limites configuráveis por plano (free / pro).

**Esforço.** ~1 fim de semana.

## Backlog / ideias soltas

Coisas que estão no radar mas sem prioridade definida:

- Agente especializado em vistos e documentação de viagem
- Integração com Google Maps para roteiros
- Exportar plano final em PDF
- Compartilhar plano via link público
- Mobile app (React Native ou PWA otimizado)
- Modo "guia local" — agente especializado num destino específico
- Modo "roadtrip" — planejamento de viagens de carro com paradas

## Como contribuir

Se algum item do roadmap te interessa:

1. Abra uma issue mencionando o item, descrevendo a abordagem que pretende seguir.
2. Aguarde alinhamento (geralmente respondo em 1-2 dias).
3. Abra um PR com a implementação.

Para sugestões de itens novos, abra uma issue com a tag `proposal`.
