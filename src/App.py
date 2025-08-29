from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from src.main.TravelAgentSystem import TravelAgentSystem
from src.main.agents.AccomodationAgent import AccomodationAgent
from src.main.agents.WeatherAgent import WeatherAgent
from src.main.tools.AccomodationTools import AccomodationTools
from src.main.tools.WeatherTools import WeatherTools

load_dotenv()

LLM = ChatGoogleGenerativeAI(model="gemini-2.5-flash", verbose=True, temperature=0.3)
# LLM2 = ChatGoogleGenerativeAI(model="gemini-2.5-flash", verbose=True, temperature=0.0)


class App:

    def __init__(self):
        pass

    @staticmethod
    def main():
        # Tools

        # Weather tools
        weather = WeatherTools()
        weather_tools = [weather.getWeather]

        # Accomodation tools
        accomodation = AccomodationTools()
        accomodation_tools = [accomodation.getAccomodation]


        #Agents

        # Weather Agent
        weatherAgent = WeatherAgent(LLM,weather_tools)
        weatherAgent.set_prompt("./main/prompts/weather_system.txt")

        # Accomodation Agent
        accomodationAgent = AccomodationAgent(LLM,accomodation_tools)
        accomodationAgent.set_prompt("./main/prompts/accomodation_system.txt")

        agents = {
            "weather_agent": weatherAgent,
            "accomodation_agent": accomodationAgent,
        }

        # Ir adicionando as ferramentas conforme o sistema for aumentando
        all_tools: list = weather_tools + accomodation_tools

        run = TravelAgentSystem(agents,all_tools)

        run.cli_mode()

if __name__ == "__main__":
    app = App()
    app.main()