# Travel Agent IA

Assistente de viagem multi-agente com LLM local (Ollama). Planeje voos, hoteis, clima e atracoes em uma conversa natural.

## Arquitetura

```
Travel-Agent/
├── backend/          Python · FastAPI · LangGraph · Ollama
│   └── src/
│       ├── agents/   WeatherAgent, TourismAgent, TransportAgent, AccomodationAgent, ManagerAgent, ConversationalAgent
│       ├── tools/    Wrappers para OpenWeatherMap, TripAdvisor, Booking.com
│       ├── prompts/  System prompts de cada agente
│       ├── graph/    Orquestracao LangGraph (StateGraph)
│       ├── api/      FastAPI REST server + auth middleware
│       └── db/       Migrations, chat_service, profile_service
└── frontend/         Next.js 16 · TypeScript · Tailwind · Framer Motion
    └── src/
        ├── app/      Pages (login, chat)
        ├── components/  UI (chat, sidebar, travel)
        ├── contexts/ AuthContext (Supabase Auth)
        ├── hooks/    useChat
        ├── lib/      Supabase client, API helpers
        └── types/    TypeScript interfaces
```

### Grafo LangGraph

![Diagrama do grafo LangGraph](docs/graph_diagram.png)

**Fluxo:** Usuario → ManagerAgent (extrai parametros) → WeatherAgent / TourismAgent / TransportAgent / AccomodationAgent → ConversationalAgent (sintese) → Resposta

## Pre-requisitos

- [Ollama](https://ollama.com) instalado e rodando
- Python 3.12+ com [uv](https://docs.astral.sh/uv/)
- Node.js 18+
- Projeto Supabase (auth + PostgreSQL)

## Instalacao

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

O servidor estara disponivel em `http://localhost:8000`.
Documentacao interativa: `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
npm install

cp .env.local.example .env.local
# Preencher .env.local com URL e anon key do Supabase

npm run dev
```

Acesse `http://localhost:3000`.

## Variaveis de ambiente

### Backend (.env)

| Variavel | Descricao | Obrigatorio |
|----------|-----------|-------------|
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key | Sim |
| `RAPID_KEY` | RapidAPI key (TripAdvisor/Booking) | Sim |
| `RAPID_HOST` | RapidAPI host | Sim |
| `OLLAMA_HOST` | URL do Ollama (default: `http://localhost:11434`) | Nao |
| `SUPABASE_URL` | URL do projeto Supabase | Sim |
| `SUPABASE_PASSWORD` | Senha do banco PostgreSQL | Sim |
| `SUPABASE_JWT_SECRET` | JWT secret para validacao de tokens | Sim |
| `SUPABASE_ANON_KEY` | Anon key (fallback de validacao) | Nao |

### Frontend (.env.local)

| Variavel | Descricao | Obrigatorio |
|----------|-----------|-------------|
| `NEXT_PUBLIC_SUPABASE_URL` | URL do projeto Supabase | Sim |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Anon/public key do Supabase | Sim |
| `NEXT_PUBLIC_API_URL` | URL do backend (default: `http://localhost:8000`) | Nao |

## API REST

### Publicos

| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| `GET` | `/health` | Health check |
| `POST` | `/api/auth/check-username` | Verifica se username existe |
| `POST` | `/api/auth/resolve-username` | Resolve username para email |

### Autenticados (Bearer token)

| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| `POST` | `/api/chat` | Enviar mensagem ao agente |
| `GET` | `/api/sessions` | Listar conversas do usuario |
| `GET` | `/api/sessions/{id}` | Carregar conversa com mensagens |
| `PATCH` | `/api/sessions/{id}` | Renomear conversa |
| `DELETE` | `/api/sessions/{id}` | Excluir conversa |

## Banco de dados (Supabase PostgreSQL)

| Tabela | Descricao |
|--------|-----------|
| `auth.users` | Usuarios (gerenciado pelo Supabase Auth) |
| `profiles` | Username, email (criado via trigger on signup) |
| `chat_sessions` | Conversas por usuario (title, timestamps) |
| `chat_messages` | Mensagens por sessao (role, content) |

Todas as tabelas tem RLS habilitado para isolamento por usuario.

## Agentes disponiveis

| Agente | Responsabilidade |
|--------|-----------------|
| `ManagerAgent` | Extrai parametros da viagem da linguagem natural |
| `WeatherAgent` | Previsao do tempo via OpenWeatherMap |
| `TourismAgent` | Atracoes e atividades via TripAdvisor |
| `TransportAgent` | Voos via TripAdvisor RapidAPI |
| `AccomodationAgent` | Hoteis via Booking.com RapidAPI |
| `ConversationalAgent` | Sintetiza todos os resultados em resposta final |

## Estendendo o sistema

### Novo agente

1. Criar `backend/src/agents/MeuAgente.py` herdando de `BaseAgent`
2. Adicionar prompt em `backend/src/prompts/`
3. Registrar em `App.build_agents()` e conectar no grafo `Graph.build_graph()`

### Nova ferramenta

1. Criar wrapper em `backend/src/tools/` usando `@tool` do LangChain
2. Passar para o agente correspondente no `App.build_agents()`
