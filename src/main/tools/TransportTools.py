import os

from amadeus import Client, ResponseError
from dotenv import load_dotenv

load_dotenv()

class TransportTools:

    def __init__(self):
        self.amadeus = Client(
            client_id=os.getenv("AMADEUS_CLIENT_ID"),
            client_secret=os.getenv("AMADEUS_CLIENT_SECRET"),
        )

    def get_flights(self):

        try:
            response = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode='GRU',
                destinationLocationCode='JFK',
                departureDate='2025-09-15',
                adults=1
            )
            print(response.data)
        except ResponseError as e:
            print(e)


if __name__ == "__main__":
    tools = TransportTools()
    tools.get_flights()