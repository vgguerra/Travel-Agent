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
            # Match [LABEL]: [VALUE] or [LABEL]: VALUE
            match = re.search(rf"\[{label}\]:\s*\[?([^\[\]\n]+?)\]?\s*$", input_text, re.MULTILINE)
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

        messages = self.prompt.format_messages(**state)
        result = self.llm.invoke(messages)
        new_data = self._capture_data(result.content.strip())

        # Merge: keep existing state values, override only with newly extracted data
        output = {"messages": result}
        for key in self.FIELD_MAP.values():
            new_value = new_data.get(key)
            existing = state.get(key)
            output[key] = new_value if new_value is not None else existing

        # Infer trip_type from return_date presence
        if output.get("return_date") is not None:
            output["trip_type"] = "IDA_VOLTA"
        elif output.get("trip_type") is None:
            output["trip_type"] = "IDA"

        # Default adults and rooms
        if output.get("adults") is None:
            output["adults"] = 1
        if output.get("rooms") is None:
            output["rooms"] = 1

        return output
