import os

from amadeus import Client, ResponseError
from dotenv import load_dotenv
from langchain_core.tools import tool
import requests

load_dotenv()

# TODO: Adicionar a feature de retornar os voos mais detalhadamente, fornecendo o itinerário, conexões, etc.

# TODO: Fazer a validação de dados que serão passados como o tipo de viagem (Round Trip ou One Way), etc.

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
            arrival_city (str): IATA code of the destination airport (e.g., 'LON').
            date (str): Departure date in format 'YYYY-MM-DD'.
            itinerary_type (str): Type of trip ('ONE_WAY' or 'ROUND_TRIP').
            adults (int): Number of adult passengers.
            num_senior (int, optional): Number of senior passengers. Defaults to 0.
            return_date (str, optional): Return date if round trip. Defaults to None.
            class_type (str, optional): Cabin class ('ECONOMY', 'BUSINESS', etc.). Defaults to "ECONOMY".

        Returns:
            List[Dict]: A list of flight options with prices and details.
        """

        # Monta a query de acordo com ida ou ida+volta
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
            querystring["returnDate"] = return_date

        headers = {
            "x-rapidapi-key": os.getenv("RAPID_KEY"),
            "x-rapidapi-host": "tripadvisor16.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()

        flights = response.json().get("data", {}).get("flights", [])

        results = []
        for i, flight in enumerate(flights, start=1):
            price = flight["purchaseLinks"][0]['totalPrice']
            results.append({
                "index": i,
                "price": price,
                # "details": flight
            })

        return results


if __name__ == "__main__":
    tools = TransportTools()
    teste = tools.getFlights(
        departure_city="GRU",   # São Paulo
        arrival_city="LON",     # Londres
        date="2025-11-01",
        itinerary_type="ONE_WAY",
        adults=1,
        class_type="ECONOMY",
    )

    print(teste)