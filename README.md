# Travel-Agent

## Propósito

O Travel-Agent é um sistema modular de agentes especializados para planejar viagens de forma assistida por LLMs. O objetivo é orquestrar múltiplos agentes — clima, transporte, hospedagem, turismo, orçamento e conversação — combinando informações de APIs externas e raciocínio de modelos para produzir roteiros, recomendações e respostas conversacionais.

## Visão geral da arquitetura

- Orquestrador: `TravelAgentSystem` responsável por receber requisições e rotear para agentes apropriados.
- Agentes: componentes especializados que expõem lógica de domínio e usam prompts + ferramentas para realizar tarefas. Exemplos:
  - `WeatherAgent` (previsão do tempo)
  - `AccomodationAgent` (hospedagem)
  - `TransportAgent` (voos/transporte)
  - `TourismAgent` (atividades/turismo)
  - `BudgetAgent` (cálculo de custos)
  - `ConversationalAgent` / `ManagerAgent` (gestão de diálogo e fluxo)
- Ferramentas: wrappers para APIs externas localizadas em `src/main/tools/`.
- Prompts: textos base que guiam o comportamento dos agentes em `src/main/prompts/`.
- Interface: CLI principal em `src/main/App.py` e interface opcional via Gradio em `src/main/interface/GradioUI.py`.

Arquitetura rápida (fluxo): Requisição -> `TravelAgentSystem` -> Router -> Agentes -> Ferramentas/APIs -> Resultado/Itinerário.

## Estrutura do projeto

- [src/main/App.py](src/main/App.py) — ponto de entrada que instância LLM, agentes e ferramentas
- [src/main/TravelAgentSystem.py](src/main/TravelAgentSystem.py) — orquestrador/router
- [src/main/agents/](src/main/agents/) — agentes especializados
- [src/main/tools/](src/main/tools/) — integrações com APIs externas (requests)
- [src/main/prompts/](src/main/prompts/) — arquivos de prompt por agente
- [src/main/interface/GradioUI.py](src/main/interface/GradioUI.py) — interface Gradio (chat)
- [src/test/](src/test/) — scripts de teste e exemplos

## Funcionalidades principais

- Geração de roteiros personalizados com base em destino, orçamento e preferências
- Requisições paralelas a serviços externos via ferramentas
- Uso de LLMs para interpretar pedidos, gerar recomendações e manter contexto de diálogo
- Extensibilidade: adicionar novos agentes e ferramentas facilmente

## Requisitos e dependências sugeridas

- Python 3.8 ou superior
- Principais bibliotecas usadas no projeto (instalar conforme necessidade):

```bash
pip install -r requirements.txt
```

Exemplo de dependências recomendadas (crie `requirements.txt` com):

```
gradio
requests
python-dotenv
langchain_core
langfuse
langchain-google-genai
```

Observação: nomes e pacotes do ecossistema LangChain / provedores de LLM podem variar; ajuste conforme provedor.

## Configuração

1. Copie/Crie um arquivo `.env` na raiz do projeto com as chaves necessárias. Exemplo:

```
GOOGLE_API_KEY=your_google_api_key
RAPID_KEY=your_rapidapi_key
```

2. Configure variáveis específicas do provedor (se estiver usando Google Generative, OpenAI etc.).

## Instalação rápida

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Se não tiver `requirements.txt`, instale manualmente as dependências mostradas acima.

## Como executar

- Executar o aplicativo principal (CLI):

```bash
python src/main/App.py
```

- Iniciar a interface Gradio (chat) — exemplo de uso integrado em `src/main/interface/GradioUI.py`:

```bash
# Abra um REPL ou script que importe e chame `gradio_interface_run(agent_talk)`
python src/main/interface/GradioUI.py
```

Detalhe: `src/main/App.py` já configura LLM (ex.: `langchain_google_genai.ChatGoogleGenerativeAI`) e registra prompts e ferramentas.

## Execução de testes simples

Alguns scripts de exemplo que usam `requests` e RapidAPI:

```bash
python src/test/tourism_test.py
python src/test/transport_test.py
```

Assegure-se de que as chaves em `.env` estejam preenchidas.

## Desenvolvimento e contribuição

- Abra uma issue para discutir features ou bugs
- Fork + branch com descrição: `feature/<nome>` ou `fix/<descrição>`
- Faça PR com testes quando possível
- Mantenha estilo do código e mensagens de commit claras

## Estendendo o sistema

- Adicionar um novo agente:
  1. Criar arquivo em `src/main/agents/` com uma classe que herde de `BaseAgent`.
  2. Adicionar prompts em `src/main/prompts/` e ferramentas em `src/main/tools/` se necessário.
  3. Registrar o agente em `src/main/App.py` e no dict de `agents` do `TravelAgentSystem`.

- Adicionar nova ferramenta: criar wrapper em `src/main/tools/` que retorne dados processáveis.

## Segurança e privacidade

- Não inclua chaves secretas no repositório. Use `.env` e variáveis de ambiente em CI.
- Valide e sanitize entradas antes de enviar para APIs externas quando necessário.
