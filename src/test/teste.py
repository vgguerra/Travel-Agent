from amadeus import Client, ResponseError
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
amadeus = Client()

response = amadeus.reference_data.locations.get(
            keyword="Lisbon",
            subType="CITY"
        )

print(response.data)

# # Datas de teste
# checkin = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
# checkout = (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d")
#
# hotels_resp = amadeus.reference_data.locations.hotels.by_city.get(cityCode="PAR")
# print(f"{len(hotels_resp.data)} hotéis encontrados.")
#
# results = []
#
# for hotel in hotels_resp.data[:50]:
#     hotel_id = hotel['hotelId']
#
#     try:
#         offers_resp = amadeus.shopping.hotel_offers_search.get(
#             hotelIds=hotel_id,
#             checkInDate=checkin,
#             checkOutDate=checkout,
#             adults=2
#         )
#
#         if not offers_resp.data:
#             print(f"No offers found for hotel id {hotel_id}")
#             continue
#
#         offer = offers_resp.data[0]
#         nome = hotel['name']
#         preco = offer['offers'][0]['price']['total']
#         moeda = offer['offers'][0]['price']['currency']
#         rating = offer['hotel'].get('rating', 'N/A')
#
#         results.append({
#             "name": nome,
#             "price": f"{preco} {moeda}",
#             "rating": rating
#         })
#
#     except ResponseError as error:
#         print("Erro da API Amadeus:", str(error))
#
# print(results)
