from datetime import datetime

import requests
from amadeus import Client
from geopy import Nominatim
from langchain_core.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()

# TODO: Implementar uma função que faça a busca automática do IATA da cidade
# TODO: Implementar uma função que verifique se a cidade tem IATA própria e caso não tenha, realize a busca dos hoteis na cidade mais próxima que tenha IATA


URL = "https://booking-com.p.rapidapi.com/v2/hotels/search-by-coordinates"

def _get_lat_long(cidade: str):
    geolocator = Nominatim(user_agent="travel_system")
    try:
        location = geolocator.geocode(cidade, timeout=10)
        if location:
            return location.latitude, location.longitude
        else:
            return None
    except Exception as e:
        print(f"Erro ao buscar coordenadas: {e}")
        return None

class AccomodationTools:

    def __init__(self):
        # Cria o client Amadeus
        self.amadeus = Client()

    @staticmethod
    @tool(
        name_or_callable="getAccomodation",
        description="Get accommodation options at the specified days and city"
    )

    def getAccomodation(adults: int,checkout_date: str,checkin_date: str,city: str, room_number: int, debug: bool = True):

        """
            Busca acomodações em uma cidade específica usando a API Rapid-Booking, retornando uma lista de hotéis com nome e preço.

            Parâmetros:
            ----------
            adults : int
                Número de adultos que irão se hospedar.
            checkout_date : str
                Data de checkout no formato 'dd/mm/YYYY' (ex: '15/10/2025').
            checkin_date : str
                Data de checkin no formato 'dd/mm/YYYY' (ex: '14/10/2025').
            city : str
                Nome da cidade onde deseja buscar acomodações (ex: 'São Paulo, Brasil').
            room_number : int
                Número de quartos necessários.
            debug : bool, opcional
                Se True, imprime informações intermediárias para depuração. Default é True.

            Retorna:
            -------
            list[str]
                Uma lista com até 10 hotéis encontrados, cada um no formato:
                "1. Nome do Hotel - Preço BRL"

            Exemplo de uso:
            ---------------
            getAccomodation(
                adults=2,
                checkout_date="15/10/2025",
                checkin_date="14/10/2025",
                city="São Paulo, Brasil",
                room_number=1
            )
        """

        checkin_fmt = datetime.strptime(checkin_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        checkout_fmt = datetime.strptime(checkout_date, "%d/%m/%Y").strftime("%Y-%m-%d")

        if debug: print(city)

        latitude,longitude = _get_lat_long(city)

        querystring = {"include_adjacency": "true","categories_filter_ids": "class::2,class::4,free_cancellation::1", "adults_number": str(adults), "checkout_date": checkout_fmt, "longitude": longitude, "room_number": str(room_number), "order_by": "price", "units": "metric", "checkin_date": checkin_fmt, "latitude": latitude, "filter_by_currency": "BRL", "locale": "pt-br"}

        headers = {
            "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
            "x-rapidapi-host": os.getenv("RAPIDAPI_HOST")
        }

        try:
            response = requests.get(URL, headers=headers, params=querystring)
            data = response.json()

            hotels = data.get("result",[])[:10]

            results =[]

            for i, hotel in enumerate(hotels, 1):
                results.append(f"{i}. {hotel["name"]} - {hotel["priceBreakdown"]["grossPrice"]["value"]} BRL")

            return results
        except Exception as e:
            print(f"Erro ao buscar acomodação: {e}")