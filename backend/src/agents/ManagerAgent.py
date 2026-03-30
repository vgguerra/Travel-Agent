import re

from src.agents.BaseAgent import BaseAgent


class ManagerAgent(BaseAgent):

    FIELD_MAP = {
        "CIDADE_SAIDA": "departure_city",
        "CIDADE_DESTINO": "destination_city",
        "DATA_IDA": "departure_date",
        "DATA_VOLTA": "return_date",
        "NUMERO_ADULTOS": "adults",
        "NUMERO_QUARTOS": "rooms",
        "TIPO_VIAGEM": "trip_type",
    }

    INT_FIELDS = {"adults", "rooms"}

    @classmethod
    def _capture_data(cls, input_text: str) -> dict:
        data = {}
        for label, key in cls.FIELD_MAP.items():
            match = re.search(rf"\[{label}\]:\s*\[(.+?)\]", input_text)
            if match:
                value = match.group(1).strip()
                if key in cls.INT_FIELDS:
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                data[key] = value
        return data

    def call(self, state):
        if self.prompt is None:
            raise ValueError("No prompt given")

        prompt = self.prompt.format(**state)
        result = self.llm.invoke(prompt)

        new_data = self._capture_data(result.content.strip())

        # Merge: keep existing state values, override only with newly extracted data
        output = {"messages": result}
        for key in self.FIELD_MAP.values():
            new_value = new_data.get(key)
            existing = state.get(key)
            output[key] = new_value if new_value is not None else existing

        return output
