from src.main.agents.BaseAgent import BaseAgent


class ManagerAgent(BaseAgent):

    @staticmethod
    def _capture_data(input_text: str) -> dict:
        data = {}

        if "[DEPARTURE_CITY]:" in input_text:
            data["departure_city"] = input_text.split("[DEPARTURE_CITY]:")[1].split("[")[1].split("]")[0]

        if "[DESTINATION_CITY]:" in input_text:
            data["destination_city"] = input_text.split("[DESTINATION_CITY]:")[1].split("[")[1].split("]")[0]

        if "[DEPARTURE_DATE]:" in input_text:
            data["departure_date"] = input_text.split("[DEPARTURE_DATE]:")[1].split("[")[1].split("]")[0]

        if "[RETURN_DATE]:" in input_text:
            data["return_date"] = input_text.split("[RETURN_DATE]:")[1].split("[")[1].split("]")[0]

        if "[NUMBER_ADULTS]:" in input_text:
            data["adults"] = int(input_text.split("[NUMBER_ADULTS]:")[1].split("[")[1].split("]")[0])

        if "[NUMBER_ROOMS]:" in input_text:
            data["rooms"] = int(input_text.split("[NUMBER_ROOMS]:")[1].split("[")[1].split("]")[0])

        if "[TRIP_TYPE]:" in input_text:
            data["trip_type"] = input_text.split("[TRIP_TYPE]:")[1].split("[")[1].split("]")[0]

        return data

    def call(self, state):

        if self.prompt is not None:
            result = (self.prompt | self.llm).invoke(state)
        else:
            raise ValueError("No prompt given")

        data = self._capture_data(result.content.strip())

        print(data)

        return {
            "messages": result,
            "departure_city": data["departure_city"],
            "destination_city": data["destination_city"],
            "departure_date": data["departure_date"],
            "return_date": data["return_date"],
            "adults": data["adults"],
            "trip_type": data["trip_type"],
            "rooms": data["rooms"],
        }
