from src.agents.BaseAgent import BaseAgent


class ConversationalAgent(BaseAgent):
    """Single point of contact with the user.

    Handles greetings, asks for missing trip data, and introduces a finished
    travel plan. To prevent the LLM from echoing the per-agent cards, we
    inject booleans into the prompt instead of the raw agent outputs.
    """

    @staticmethod
    def _flag(value) -> str:
        return "sim" if value not in (None, "", []) else "nao"

    def call(self, state):
        if self.prompt is None:
            raise ValueError("No prompt given")

        # Derive flags so the prompt can branch on what is/isn't available
        # without ever seeing the raw weather/tourism/transport/accommodation text.
        derived = dict(state)
        derived["has_weather"] = self._flag(state.get("weather"))
        derived["has_tourism"] = self._flag(state.get("tourism"))
        derived["has_transport"] = self._flag(state.get("transport"))
        derived["has_accommodation"] = self._flag(state.get("accommodation"))

        prompt = self.prompt.format_messages(**derived)
        result = self.llm.invoke(prompt)
        return {"messages": result}
