import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from src.TravelAgentSystem import TravelAgentSystem
from src.agents.AccomodationAgent import AccomodationAgent
from src.agents.ConversationalAgent import ConversationalAgent
from src.agents.TourismAgent import TourismAgent
from src.agents.TransportAgent import TransportAgent
from src.agents.WeatherAgent import WeatherAgent
from src.agents.ManagerAgent import ManagerAgent
from src.tools.AccomodationTools import AccomodationTools
from src.tools.TourismTools import TourismTools
from src.tools.TransportTools import TransportTools
from src.tools.WeatherTools import WeatherTools

load_dotenv()

LLM = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
    temperature=0.3,
    num_predict=2048,
)


class App:

    def __init__(self):
        pass

    @staticmethod
    def build_agents():
        weather = WeatherTools()
        weather_tools = [weather.getWeather]

        accomodation = AccomodationTools()
        accomodation_tools = [accomodation.getAccomodation]

        transport = TransportTools()
        transport_tools = [transport.getFlights]

        tourism = TourismTools()
        tourism_tools = [tourism.getTourismIdeas]

        base_prompt_path = "./src/prompts"

        weatherAgent = WeatherAgent(LLM, weather_tools)
        weatherAgent.set_prompt(f"{base_prompt_path}/weather_system.txt")

        accomodationAgent = AccomodationAgent(LLM, accomodation_tools)
        accomodationAgent.set_prompt(f"{base_prompt_path}/accomodation_system.txt")

        transportAgent = TransportAgent(LLM, transport_tools)
        transportAgent.set_prompt(f"{base_prompt_path}/transport_system.txt")

        tourismAgent = TourismAgent(LLM, tourism_tools)
        tourismAgent.set_prompt(f"{base_prompt_path}/tourism_system.txt")

        managerAgent = ManagerAgent(LLM)
        managerAgent.set_prompt(f"{base_prompt_path}/manager_system.txt")

        conversationalAgent = ConversationalAgent(LLM)
        conversationalAgent.set_prompt(f"{base_prompt_path}/conversational_system.txt")

        agents = {
            "weather_agent": weatherAgent,
            "accomodation_agent": accomodationAgent,
            "transport_agent": transportAgent,
            "tourism_agent": tourismAgent,
            "manager_agent": managerAgent,
            "conversational_agent": conversationalAgent,
        }

        all_tools: dict = {
            "weather": weather_tools,
            "accomodation": accomodation_tools,
            "transport": transport_tools,
            "tourism": tourism_tools,
        }

        return agents, all_tools

    @staticmethod
    def cli():
        """Start the interactive CLI mode."""
        agents, all_tools = App.build_agents()
        run = TravelAgentSystem(agents, all_tools)
        run.cli_mode()
