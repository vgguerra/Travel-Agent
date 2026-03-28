import os
import requests
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY")
BASE_URL_FORECAST: str = "https://api.openweathermap.org/data/2.5/forecast"

class WeatherTools:

    def __init__(self):
        pass

    @staticmethod
    @tool(name_or_callable="getWeather", description="Get Weather Forecast for the next X days from Weather API")
    def getWeather(city: str, days: int) -> str:

        """
            Returns the weather forecast for a specific city for the next X days.

            Args:
                city (str): Name of the city to get the forecast for.
                days (int): Number of days to return the forecast for (maximum 5 for this endpoint).

            Returns:
                str: A summarized list of weather forecasts for the requested period.
        """

        if OPENWEATHER_API_KEY is None or BASE_URL_FORECAST is None:
            raise Exception('API key and base url must be set')

        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "pt_br",
        }

        try:
            response = requests.get(BASE_URL_FORECAST, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('cod') == "200":
                forecasts = data['list']

                results = []
                max_entries = days * 8
                for forecast in forecasts[:max_entries]:
                    dt_txt = forecast['dt_txt']
                    temp = forecast['main']['temp']
                    desc = forecast['weather'][0]['description']
                    results.append(f"{dt_txt}: {temp}°C, {desc}")

                return "\n".join(results)

            else:
                return f"Erro da API: {data.get('message', 'Erro desconhecido')}"

        except requests.exceptions.Timeout:
            return f"A requisição para a API de previsão em {city} excedeu o tempo limite."

        except requests.exceptions.RequestException as e:
            return f"Erro ao conectar à API de previsão para {city}: {e}. Verifique sua conexão ou chave de API."

        except Exception as e:
            return f"Ocorreu um erro inesperado ao processar a previsão para {city}: {e}"
