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


URL = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotelsByCoordinates"

def _get_lat_long(cidade: str):
    geolocator = Nominatim(user_agent="main")
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
                checkin_date="2025-09-24",
                checkout_date="2025-09-28",
                city="São Paulo, Brasil",
                room_number=1
            )
        """


        latitude,longitude = _get_lat_long(city)

        querystring = {"latitude": latitude, "longitude": longitude, "adults_number": str(adults), "departure_date": checkout_date, "room_qty": str(room_number), "units": "metric", "arrival_date": checkin_date, "currency_code": "BRL", "languagecode": "pt-br","location":"BR"}

        headers = {
            "x-rapidapi-key": os.getenv("RAPID_KEY"),
            "x-rapidapi-host": os.getenv("RAPID_HOST")
        }

        try:
            response = requests.get(URL, headers=headers, params=querystring)
            data = response.json()

            hotels = data["data"]["result"]

            results =[]

            for i, hotel in enumerate(hotels, 1):
                results.append(f"{i}. {hotel["hotel_name"]} - {hotel["composite_price_breakdown"]["net_amount"]["value"]} BRL")

            return results
        except Exception as e:
            print(f"Erro ao buscar acomodação: {e}")