import requests
from geopy import Nominatim
from langchain_core.tools import tool

from src.config import settings

URL = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotelsByCoordinates"

def _get_lat_long(cidade: str):
    geolocator = Nominatim(user_agent="main")
    try:
        location = geolocator.geocode(cidade, timeout=10)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception:
        return None, None

class AccomodationTools:

    @staticmethod
    @tool(
        name_or_callable="getAccomodation",
        description="Get accommodation options at the specified days and city"
    )
    def getAccomodation(adults: int, checkout_date: str, checkin_date: str, city: str, room_number: int):
        """
        Busca acomodações em uma cidade específica usando a API Rapid-Booking.

        Args:
            adults (int): Número de adultos.
            checkout_date (str): Data de checkout no formato 'YYYY-MM-DD'.
            checkin_date (str): Data de checkin no formato 'YYYY-MM-DD'.
            city (str): Nome da cidade (ex: 'Rio de Janeiro, Brasil').
            room_number (int): Número de quartos.

        Returns:
            list[str]: Lista de hotéis com nome e preço.
        """

        latitude, longitude = _get_lat_long(city)
        if latitude is None:
            return f"Não foi possível encontrar as coordenadas de '{city}'."

        querystring = {
            "latitude": latitude,
            "longitude": longitude,
            "adults_number": str(adults),
            "departure_date": checkout_date,
            "room_qty": str(room_number),
            "units": "metric",
            "arrival_date": checkin_date,
            "currency_code": "BRL",
            "languagecode": "pt-br",
            "location": "BR",
        }

        headers = {
            "x-rapidapi-key": settings.RAPID_KEY,
            "x-rapidapi-host": settings.RAPID_HOST,
        }

        try:
            response = requests.get(URL, headers=headers, params=querystring, timeout=20)
            response.raise_for_status()
            data = response.json()

            hotels = data.get("data", {}).get("result", [])
            if not hotels:
                return "Nenhuma acomodação encontrada para os critérios informados."

            results = []
            for i, hotel in enumerate(hotels[:10], 1):
                name = hotel.get("hotel_name", "Hotel desconhecido")
                price = hotel.get("composite_price_breakdown", {}).get("net_amount", {}).get("value")
                if price:
                    results.append(f"{i}. {name} - R$ {price:.2f}")
                else:
                    results.append(f"{i}. {name} - Preço não disponível")

            return results

        except requests.exceptions.Timeout:
            return "A busca de hospedagem excedeu o tempo limite. Tente novamente mais tarde."
        except requests.exceptions.RequestException:
            return "Erro ao buscar hospedagem: serviço temporariamente indisponível."
        except Exception as e:
            return f"Erro inesperado ao buscar hospedagem: {str(e)}"
