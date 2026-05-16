"""Factory de LLM. Seleciona o provedor com base em settings.LLM_PROVIDER."""
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from src.config import settings


def build_llm(
    provider: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> BaseChatModel:
    """Constrói o LLM. Parâmetros sobrescrevem os defaults de settings."""
    provider = (provider or settings.LLM_PROVIDER).lower()
    temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
    max_tokens = max_tokens if max_tokens is not None else settings.LLM_MAX_TOKENS

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=model or settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_HOST,
            temperature=temperature,
            num_predict=max_tokens,
        )

    if provider == "google":
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY não definido no .env")

        return ChatGoogleGenerativeAI(
            model=model or settings.GOOGLE_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

    if provider == "openrouter":
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY não definido no .env")

        return ChatOpenAI(
            model=model or settings.OPENROUTER_MODEL,
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    raise ValueError(
        f"LLM_PROVIDER inválido: {provider!r}. "
        "Use 'ollama', 'google' ou 'openrouter'."
    )
