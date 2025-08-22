import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from src.travel_system.TravelAgentSystem import TravelAgentSystem
from src.travel_system.agents.WeatherAgent import WeatherAgent
from src.travel_system.tools.WeatherTools import WeatherTools

load_dotenv()

LLM = ChatGoogleGenerativeAI(model="gemini-2.5-flash", verbose=True, temperature=0.3)
# LLM2 = ChatGoogleGenerativeAI(model="gemini-2.5-flash", verbose=True, temperature=0.0)


class App:

    def __init__(self):
        pass

    @staticmethod
    def main():
        weather = WeatherTools()
        weather_tools = [weather.getWeather]

        # Weather Agent
        weatherAgent = WeatherAgent(LLM,weather_tools)
        weatherAgent.set_prompt("./travel_system/prompts/weather_system.txt")

        agents = {
            "weather_agent": weatherAgent,
        }

        # Ir adicionando as ferramentas conforme o sistema for aumentando
        all_tools: list = weather_tools

        run = TravelAgentSystem(agents,all_tools)

        run.cli_mode()

if __name__ == "__main__":
    app = App()
    app.main()