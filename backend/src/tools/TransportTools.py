import os

from dotenv import load_dotenv
from langchain_core.tools import tool
from datetime import datetime
import requests

load_dotenv()

url = "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchFlights"

class TransportTools:

    @staticmethod
    @tool(
        name_or_callable="getFlights",
        description="Get flights at the specified days and city"
    )
    def getFlights(
            departure_city: str,
            arrival_city: str,
            date: str,
            itinerary_type: str,
            adults: int,
            num_senior: int = 0,
            return_date: str = None,
            class_type: str = "ECONOMY"
    ):
        """
        Search for flight options using the TripAdvisor RapidAPI endpoint.

        Args:
            departure_city (str): IATA code of the origin airport (e.g., 'GRU').
            arrival_city (str): IATA code of the destination airport (e.g., 'GIG').
            date (str): Departure date in format 'YYYY-MM-DD'.
            itinerary_type (str): Type of trip ('ONE_WAY' or 'ROUND_TRIP').
            adults (int): Number of adult passengers.
            num_senior (int, optional): Number of senior passengers. Defaults to 0.
            return_date (str, optional): Return date if round trip. Defaults to None.
            class_type (str, optional): Cabin class ('ECONOMY', 'BUSINESS', PREMIUM_ECONOMY or FIRST). Defaults to "ECONOMY".

        Returns:
            List[Dict]: A list of flight options with prices and details.
        """

        allowed_classes = ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"]
        if class_type not in allowed_classes:
            return f"Erro: class_type inválido. Escolha entre: {', '.join(allowed_classes)}"

        def validate_date(date_str):
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                return False
            return True

        if not validate_date(date):
            return f"Erro: Data inválida: {date}. Use o formato YYYY-MM-DD."

        querystring = {
            "sourceAirportCode": departure_city,
            "destinationAirportCode": arrival_city,
            "date": date,
            "itineraryType": itinerary_type,
            "sortOrder": "PRICE",
            "numAdults": str(adults),
            "numSeniors": num_senior,
            "classOfService": class_type,
            "pageNumber": "1",
            "nearby": "yes",
            "nonstop": "yes",
            "currencyCode": "BRL"
        }

        if return_date:
            if not validate_date(return_date):
                return f"Erro: Data de retorno inválida: {return_date}. Use o formato YYYY-MM-DD."
            querystring["returnDate"] = return_date

        headers = {
            "x-rapidapi-key": os.getenv("RAPID_KEY"),
            "x-rapidapi-host": "tripadvisor16.p.rapidapi.com"
        }

        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=15)
            response.raise_for_status()
            data = response.json()

            if not data.get("status", True):
                return "A API de voos está temporariamente indisponível. Não foi possível buscar passagens aéreas no momento."

            flights = data.get("data", {}).get("flights", [])
            if not flights:
                return "Nenhum voo encontrado para os critérios informados."

            results = []
            for i, flight in enumerate(flights[:10], start=1):
                price = flight["purchaseLinks"][0]["totalPrice"]
                results.append({
                    "index": i,
                    "price": price,
                    "details": flight
                })
            return results

        except requests.exceptions.Timeout:
            return "A busca de voos excedeu o tempo limite. Tente novamente mais tarde."
        except requests.exceptions.RequestException as e:
            return f"Erro ao buscar voos: serviço temporariamente indisponível."
        except Exception as e:
            return f"Erro inesperado ao buscar voos: {str(e)}"
