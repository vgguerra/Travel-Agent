# Travel Agent IA

Assistente de viagem multi-agente com LLM local (Ollama). Planeje voos, hotéis, clima e atrações em uma conversa natural.

## Arquitetura

```
Travel-Agent/
├── backend/          Python · FastAPI · LangGraph · Ollama
│   └── src/main/
│       ├── agents/   WeatherAgent, TourismAgent, TransportAgent, AccomodationAgent, ManagerAgent, ConversationalAgent
│       ├── tools/    Wrappers para OpenWeatherMap, TripAdvisor, Booking.com
│       ├── prompts/  System prompts de cada agente
│       ├── graph/    Orquestração LangGraph (StateGraph)
│       └── api/      FastAPI REST server
└── frontend/         Next.js 16 · TypeScript · Tailwind · Framer Motion
```

**Fluxo:** Usuário → ManagerAgent (extrai parâmetros) → WeatherAgent / TourismAgent / TransportAgent / AccomodationAgent → ConversationalAgent (síntese) → Resposta

## Pré-requisitos

- [Ollama](https://ollama.com) instalado e rodando
- Python 3.12+ com [uv](https://docs.astral.sh/uv/)
- Node.js 18+

## Instalação

### 1. Ollama + modelo

```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Baixar modelo (llama3.2 ~2GB)
ollama pull llama3.2

# Iniciar servidor
ollama serve
```

### 2. Backend

```bash
cd backend

# Instalar dependências
uv sync

# Copiar e preencher variáveis de ambiente
cp .env.example .env
# Editar .env com suas chaves de API

# Iniciar servidor FastAPI
uv run uvicorn src.main.api.server:app --reload --port 8000
```

O servidor estará disponível em `http://localhost:8000`.
Documentação interativa: `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend

npm install
npm run dev
```

Acesse `http://localhost:3000`.

## Variáveis de ambiente (backend/.env)

| Variável | Descrição | Obrigatório |
|----------|-----------|-------------|
| `API_KEY` | OpenWeatherMap API key | Sim (para clima) |
| `RAPID_KEY` | RapidAPI key (TripAdvisor/Booking) | Sim (para voos/hotéis) |
| `RAPID_HOST` | RapidAPI host | Sim |
| `OLLAMA_HOST` | URL do Ollama (default: `http://localhost:11434`) | Não |

## API REST

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health` | Health check |
| `POST` | `/api/chat` | Enviar mensagem ao agente |
| `DELETE` | `/api/session/{id}` | Limpar sessão |

### Exemplo de request

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Quero viajar de São Paulo para Florianópolis em julho"}'
```

## Estendendo o sistema

### Novo agente

1. Criar `backend/src/main/agents/MeuAgente.py` herdando de `BaseAgent`
2. Adicionar prompt em `backend/src/main/prompts/`
3. Registrar em `App.build_agents()` e conectar no grafo `Graph.build_graph()`

### Nova ferramenta

1. Criar wrapper em `backend/src/main/tools/` usando `@tool` do LangChain
2. Passar para o agente correspondente no `App.build_agents()`

## Agentes disponíveis

| Agente | Responsabilidade |
|--------|-----------------|
| `ManagerAgent` | Extrai parâmetros da viagem da linguagem natural |
| `WeatherAgent` | Previsão do tempo via OpenWeatherMap |
| `TourismAgent` | Atrações e atividades via TripAdvisor |
| `TransportAgent` | Voos via TripAdvisor RapidAPI |
| `AccomodationAgent` | Hotéis via Booking.com RapidAPI |
| `ConversationalAgent` | Sintetiza todos os resultados em resposta final |
