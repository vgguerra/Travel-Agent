from datetime import datetime
from amadeus import Client, ResponseError
from langchain_core.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()

# TODO: Implementar uma função que faça a busca automática do IATA da cidade
# TODO: Implementar uma função que verifique se a cidade tem IATA própria e caso não tenha, realize a busca dos hoteis na cidade mais próxima que tenha IATA

class AccomodationTools:

    def __init__(self):
        # Cria o client Amadeus
        self.amadeus = Client()

    @staticmethod
    @tool(
        name_or_callable="getAccomodation",
        description="Get accommodation options at the specified days and city"
    )
    def getAccomodation(city: str,
                        checkin: str,
                        checkout: str,
                        type_: str = None,
                        adults: int = 1,
                        debug: bool = True):
        """
        Busca acomodações reais via Amadeus API.
        Retorna lista de hotéis com nome, preço e rating.
        """
        try:
            service = AccomodationTools()
            amadeus = service.amadeus

            # 1. Obter cityCode (IATA)
            city_resp = amadeus.reference_data.locations.get(
                keyword=city,
                subType="CITY"
            )
            if not city_resp.data:
                if debug: print("Cidade não encontrada.")
                return []

            city_code = city_resp.data[0]["iataCode"]
            if debug: print("City code:", city_code)

            checkin_fmt = datetime.strptime(checkin, "%d/%m/%Y").strftime("%Y-%m-%d")
            checkout_fmt = datetime.strptime(checkout, "%d/%m/%Y").strftime("%Y-%m-%d")

            if debug:
                print("Checkin:", checkin_fmt, "Checkout:", checkout_fmt)

            hotels_resp = amadeus.reference_data.locations.hotels.by_city.get(cityCode=city_code)
            if debug: print(f"{len(hotels_resp.data)} hotéis encontrados.")

            results = []
            for hotel in hotels_resp.data[:10]:
                hotel_id = hotel['hotelId']

                try:
                    offers_resp = amadeus.shopping.hotel_offers_search.get(
                        hotelIds=hotel_id,
                        checkInDate=checkin_fmt,
                        checkOutDate=checkout_fmt,
                        adults=adults
                    )

                    if not offers_resp.data:
                        continue

                    offer = offers_resp.data[0]
                    nome = hotel['name']
                    preco = offer['offers'][0]['price']['total']
                    moeda = offer['offers'][0]['price']['currency']
                    rating = offer['hotel'].get('rating', 'N/A')

                    if type_ and type_.lower() not in nome.lower():
                        continue

                    results.append({
                        "name": nome,
                        "price": f"{preco} {moeda}",
                        "rating": rating
                    })

                except ResponseError as e:
                    if debug: print(f"Erro ao buscar ofertas do hotel {hotel['name']}: {e}")

            return results

        except ResponseError as error:
            if debug: print("Erro da API Amadeus:", str(error))
            return []
