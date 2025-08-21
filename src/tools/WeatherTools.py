import requests
from langchain_core.tools import tool

class WeatherTools:

    API_KEY: str = None
    BASE_URL: str = None

    def __init__(self,API_KEY,BASE_URL):
        self.API_KEY = API_KEY
        self.BASE_URL = BASE_URL

    @tool(name_or_callable="getWeather",description="Get Weather from Weather API")
    def getWeather(self, city: str) -> str:
        """
        Retorna a previsão do tempo para uma cidade específica.

        Parâmetros:
        - city (str): Nome da cidade a consultar.

        Retorna:
        - str: Descrição do clima com temperatura, sensação térmica e condição climática.
        """
        if self.API_KEY is None or self.BASE_URL is None:
            raise Exception('API key and base url must be set')

        params = {
            "q": city,
            "key": self.API_KEY,
            "units": "metric",
            "lang": "pt-br",
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('cod') == 200:
                temperature = data['main']['temp']
                feels_like = data['main']['feels_like']
                description = data['weather'][0]['description']
                city_name = data['name']
                country = data['sys']['country']

                return (
                    f"O tempo em {city_name}, {country} é de {temperature}°C (sensação de {feels_like}°C) "
                    f"com {description}."
                )

            elif data.get('cod') == '404':
                return f"Não foi possível encontrar a cidade '{city}'. Verifique o nome e tente novamente."

            else:
                return f"Não foi possível obter informações detalhadas do tempo para {city}. Erro da API: {data.get('message', 'Erro desconhecido')}"

        except requests.exceptions.Timeout:
            return f"A requisição para a API de tempo em {city} excedeu o tempo limite."

        except requests.exceptions.RequestException as e:
            return f"Erro ao conectar à API de tempo para {city}: {e}. Verifique sua conexão ou chave de API."

        except Exception as e:
            return f"Ocorreu um erro inesperado ao processar o tempo para {city}: {e}"