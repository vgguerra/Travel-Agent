# Travel Agent IA

[![Python](https://img.shields.io/badge/python-3.12+-blue)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.x-orange)](https://github.com/langchain-ai/langgraph)
[![Status](https://img.shields.io/badge/status-active%20development-yellow)](#)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> 🌐 [English](README.md) · **Português**

Assistente de viagem multi-agente com LLM local (Ollama). Você descreve a viagem em linguagem natural e seis agentes especializados se coordenam para retornar um plano com voos, hospedagem, clima, atrações e estimativa de custo.

> **Em desenvolvimento ativo.** Projeto pessoal de portfólio. Por enquanto vive só no GitHub, sem deploy público — para experimentar, é necessário rodar localmente.

## Motivação

A maior parte dos clones de assistentes conversacionais resolve o problema com um único modelo de uso geral. Este projeto explora o caminho oposto: dividir uma tarefa complexa (planejar uma viagem) em agentes especializados, orquestrá-los com LangGraph e ver até onde dá pra ir só com um LLM rodando local (qwen2.5:7b via Ollama).

Também funciona como sandbox para estudar padrões de agentic AI — extração de parâmetros, tool-use, síntese conversacional, observabilidade — antes de aplicá-los em contextos profissionais.

## Arquitetura

```
Travel-Agent/
├── backend/          Python · FastAPI · LangGraph · Ollama
│   └── src/
│       ├── agents/   Manager, Weather, Tourism, Transport, Accomodation, Budget, Conversational
│       ├── tools/    Wrappers para OpenWeatherMap, TripAdvisor, Booking.com
│       ├── prompts/  System prompts de cada agente
│       ├── graph/    Orquestração LangGraph (StateGraph)
│       ├── api/      Servidor FastAPI REST + middleware de auth
│       └── db/       Migrations, chat_service, profile_service
└── frontend/         Next.js 16 · TypeScript · Tailwind · Framer Motion
    └── src/
        ├── app/      Páginas (login, chat)
        ├── components/  UI (chat, sidebar, travel)
        ├── contexts/ AuthContext (Supabase Auth)
        ├── hooks/    useChat
        ├── lib/      Cliente Supabase, helpers de API
        └── types/    Interfaces TypeScript
```

### Grafo LangGraph

![Diagrama do grafo LangGraph](docs/graph_diagram.png)

**Fluxo:** Usuário → ManagerAgent (extrai parâmetros) → WeatherAgent / TourismAgent / TransportAgent / AccomodationAgent / BudgetAgent (em paralelo) → ConversationalAgent (síntese) → Resposta

Para uma descrição mais aprofundada da arquitetura, ver [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Pré-requisitos

- [Ollama](https://ollama.com) instalado e rodando
- Python 3.12+ com [uv](https://docs.astral.sh/uv/)
- Node.js 18+
- Projeto Supabase (auth + PostgreSQL)
- Chaves de API: OpenWeatherMap e RapidAPI (TripAdvisor / Booking.com)

## Instalação

### 1. Ollama + modelo

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:7b
ollama serve
```

### 2. Backend

```bash
cd backend
uv sync

cp .env.example .env
# Preencher .env com as chaves

uv run uvicorn src.api.server:app --reload --port 8000
```

O servidor estará disponível em `http://localhost:8000`.
Documentação interativa: `http://localhost:8000/docs`.

### 3. Frontend

```bash
cd frontend
npm install

cp .env.local.example .env.local
# Preencher .env.local com URL e anon key do Supabase

npm run dev
```

Acesse `http://localhost:3000`.

## Variáveis de ambiente

### Backend (`.env`)

| Variável | Descrição | Obrigatório |
|----------|-----------|-------------|
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key | Sim |
| `RAPID_KEY` | RapidAPI key (TripAdvisor / Booking) | Sim |
| `RAPID_HOST` | RapidAPI host | Sim |
| `OLLAMA_HOST` | URL do Ollama (default: `http://localhost:11434`) | Não |
| `SUPABASE_URL` | URL do projeto Supabase | Sim |
| `SUPABASE_PASSWORD` | Senha do banco PostgreSQL | Sim |
| `SUPABASE_JWT_SECRET` | JWT secret para validação de tokens | Sim |
| `SUPABASE_ANON_KEY` | Anon key (fallback de validação) | Não |

### Frontend (`.env.local`)

| Variável | Descrição | Obrigatório |
|----------|-----------|-------------|
| `NEXT_PUBLIC_SUPABASE_URL` | URL do projeto Supabase | Sim |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Anon / public key do Supabase | Sim |
| `NEXT_PUBLIC_API_URL` | URL do backend (default: `http://localhost:8000`) | Não |

## API REST

### Públicos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health` | Health check |
| `POST` | `/api/auth/check-username` | Verifica se username existe |
| `POST` | `/api/auth/resolve-username` | Resolve username para email |

### Autenticados (Bearer token)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/chat` | Enviar mensagem ao agente |
| `GET` | `/api/sessions` | Listar conversas do usuário |
| `GET` | `/api/sessions/{id}` | Carregar conversa com mensagens |
| `PATCH` | `/api/sessions/{id}` | Renomear conversa |
| `DELETE` | `/api/sessions/{id}` | Excluir conversa |

## Banco de dados (Supabase PostgreSQL)

| Tabela | Descrição |
|--------|-----------|
| `auth.users` | Usuários (gerenciado pelo Supabase Auth) |
| `profiles` | Username, email (criado via trigger no signup) |
| `chat_sessions` | Conversas por usuário (title, timestamps) |
| `chat_messages` | Mensagens por sessão (role, content) |

Todas as tabelas têm RLS habilitado para isolamento por usuário.

## Agentes disponíveis

| Agente | Responsabilidade |
|--------|------------------|
| `ManagerAgent` | Extrai parâmetros da viagem da linguagem natural |
| `WeatherAgent` | Previsão do tempo via OpenWeatherMap |
| `TourismAgent` | Atrações e atividades via TripAdvisor |
| `TransportAgent` | Voos via TripAdvisor RapidAPI |
| `AccomodationAgent` | Hotéis via Booking.com RapidAPI |
| `BudgetAgent` | Estimativa de custo total da viagem |
| `ConversationalAgent` | Sintetiza todos os resultados em resposta final |

## Observabilidade

A aplicação está instrumentada com [Langfuse](https://langfuse.com) para rastrear chamadas dos agentes (latência, tokens, prompts, tool calls). É opcional — sem chaves Langfuse o projeto roda normalmente, com tracing local desligado.

## Roadmap

Itens em ordem aproximada de prioridade:

- Tool-use mais robusto, com ferramentas dinâmicas por agente
- Memória persistente entre sessões
- Avaliação dos agentes, aplicando o framework do curso *Evaluating AI Agents* da DeepLearning.AI
- UI com indicação visual das tool calls em tempo real
- Suporte a múltiplos provedores de LLM além do Ollama (OpenAI, Anthropic)
- Testes de integração e2e
- Deploy público (Vercel para frontend, Fly.io ou Azure para backend)

Versão detalhada com critérios de aceitação em [docs/ROADMAP.md](docs/ROADMAP.md).

## Estendendo o sistema

### Novo agente

1. Criar `backend/src/agents/MeuAgente.py` herdando de `BaseAgent`.
2. Adicionar prompt em `backend/src/prompts/`.
3. Registrar em `App.build_agents()` e conectar no grafo `Graph.build_graph()`.

### Nova ferramenta

1. Criar wrapper em `backend/src/tools/` usando `@tool` do LangChain.
2. Passar para o agente correspondente em `App.build_agents()`.

## Como contribuir

O projeto está em desenvolvimento ativo e contribuições são bem-vindas. Algumas formas de ajudar:

- Dar uma star no repo (ajuda na descoberta)
- Abrir uma issue descrevendo um bug, dúvida ou ideia
- Propor uma nova capacidade ou agente
- Abrir um PR — para mudanças não triviais, recomendo abrir uma issue antes para alinharmos a abordagem
- Trocar uma ideia comigo sobre orquestração multiagente

Antes de abrir um PR, vale dar uma olhada no [roadmap](docs/ROADMAP.md) para ver onde a contribuição se encaixa.

## Licença

MIT — ver [LICENSE](LICENSE).
