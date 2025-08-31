import os

from amadeus import Client, ResponseError
from dotenv import load_dotenv
import requests

load_dotenv()


def amadeus():

    amadeus = Client(client_id=os.getenv("AMADEUS_CLIENT_ID"),
                client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
    )

    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode='FLN',
            destinationLocationCode='GRU',
            departureDate='2025-11-01',
            adults=1,
            currencyCode='BRL',
        )
        print(response.data[:1])
    except ResponseError as error:
        print(error)


def trip_advisor():

    url = "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchFlights"

    querystring = {"sourceAirportCode": "FLN", "destinationAirportCode": "LON", "date": "2025-10-01",
                   "itineraryType": "ROUND_TRIP", "sortOrder": "PRICE", "numAdults": "1", "numSeniors": "0",
                   "classOfService": "ECONOMY", "returnDate": "2025-10-06", "pageNumber": "1", "nearby": "yes",
                   "nonstop": "yes", "currencyCode": "BRL"}

    headers = {
        "x-rapidapi-key": os.getenv("RAPID_KEY"),
        "x-rapidapi-host": "tripadvisor16.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    flights = response.json()["data"]["flights"]



    for i, flight in enumerate(flights, 0):
        print(f"{i}. PREÇO IDA E VOLTA- {flight['purchaseLinks'][0]["totalPrice"]}")

if __name__ == '__main__':
    trip_advisor()