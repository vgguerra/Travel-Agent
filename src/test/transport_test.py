import os

from amadeus import Client, ResponseError
from dotenv import load_dotenv

load_dotenv()

amadeus = Client(client_id=os.getenv("AMADEUS_CLIENT_ID"),
            client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
)

try:
    response = amadeus.shopping.flight_offers_search.get(
        originLocationCode='MAD',
        destinationLocationCode='LON',
        departureDate='2025-11-01',
        adults=1)
    print(response.data)
except ResponseError as error:
    print(error)