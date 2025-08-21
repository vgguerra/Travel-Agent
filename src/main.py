from langchain_google_genai import ChatGoogleGenerativeAI

from src.agents.BaseAgent import BaseAgent
from src.agents.WeatherAgent import WeatherAgent
from src.tools.WeatherTools import WeatherTools
from src.TravelSystem.App import App

LLM = ChatGoogleGenerativeAI(model="gemini-2.5-flash", verbose=True, temperature=0.3)

if __name__ == "__main__":
    weather_tools = WeatherTools(API_KEY="0", BASE_URL="=")
    tools = [weather_tools.getWeather]

    weather_agent = WeatherAgent(LLM,tools)
    weather_agent.set_prompt("./prompts/weather_system.txt")

    agents: dict[str, BaseAgent] = {
        "weather_agent": weather_agent
    }



    weather_tools = WeatherTools(API_KEY = "0", BASE_URL = "=")

    print("Prompt:", agents["weather_agent"].prompt)
    print("Tools:", tools)

    app = App(agents, tools)

    app.cli_mode()

