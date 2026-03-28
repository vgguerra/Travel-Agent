from src.main.agents.BaseAgent import BaseAgent


class ManagerAgent(BaseAgent):

    @staticmethod
    def _capture_data(input_text: str) -> dict:
        data = {}

        if "[CIDADE_SAIDA]:" in input_text:
            data["departure_city"] = input_text.split("[CIDADE_SAIDA]:")[1].split("[")[1].split("]")[0]

        if "[CIDADE_DESTINO]:" in input_text:
            data["destination_city"] = input_text.split("[CIDADE_DESTINO]:")[1].split("[")[1].split("]")[0]

        if "[DATA_IDA]:" in input_text:
            data["departure_date"] = input_text.split("[DATA_IDA]:")[1].split("[")[1].split("]")[0]

        if "[DATA_VOLTA]:" in input_text:
            data["return_date"] = input_text.split("[DATA_VOLTA]:")[1].split("[")[1].split("]")[0]

        if "[NUMERO_ADULTOS]:" in input_text:
            try:
                data["adults"] = int(input_text.split("[NUMERO_ADULTOS]:")[1].split("[")[1].split("]")[0])
            except ValueError:
                data["adults"] = None

        if "[NUMERO_QUARTOS]:" in input_text:
            try:
                data["rooms"] = int(input_text.split("[NUMERO_QUARTOS]:")[1].split("[")[1].split("]")[0])
            except ValueError:
                data["rooms"] = None

        if "[TIPO_VIAGEM]:" in input_text:
            data["trip_type"] = input_text.split("[TIPO_VIAGEM]:")[1].split("[")[1].split("]")[0]

        return data

    def call(self, state):

        if self.prompt is not None:
            prompt = self.prompt.format(**state)
            result = self.llm.invoke(prompt)
        else:
            raise ValueError("No prompt given")

        data = self._capture_data(result.content.strip())

        return {
            "messages": result,
            "departure_city": data.get("departure_city"),
            "destination_city": data.get("destination_city"),
            "departure_date": data.get("departure_date"),
            "return_date": data.get("return_date"),
            "adults": data.get("adults"),
            "trip_type": data.get("trip_type"),
            "rooms": data.get("rooms"),
        }
