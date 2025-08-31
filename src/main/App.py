from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from src.main.TravelAgentSystem import TravelAgentSystem
from src.main.agents.AccomodationAgent import AccomodationAgent
from src.main.agents.TransportAgent import TransportAgent
from src.main.agents.WeatherAgent import WeatherAgent
from src.main.tools.AccomodationTools import AccomodationTools
from src.main.tools.TransportTools import TransportTools
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

        transport = TransportTools()
        transport_tools = [transport.getFlights]


        #Agents

        # Weather Agent
        weatherAgent = WeatherAgent(LLM,weather_tools)
        weatherAgent.set_prompt("./prompts/weather_system.txt")

        # Accomodation Agent
        accomodationAgent = AccomodationAgent(LLM,accomodation_tools)
        accomodationAgent.set_prompt("./prompts/accomodation_system.txt")

        # Transport Agent
        transportAgent = TransportAgent(LLM,transport_tools)
        transportAgent.set_prompt("./prompts/transport_system.txt")

        agents = {
            "weather_agent": weatherAgent,
            "accomodation_agent": accomodationAgent,
            "transport_agent": transportAgent,
        }

        # Ir adicionando as ferramentas conforme o sistema for aumentando
        all_tools: list = weather_tools + accomodation_tools + transport_tools

        run = TravelAgentSystem(agents,all_tools)

        run.cli_mode()

if __name__ == "__main__":
    app = App()
    app.main()