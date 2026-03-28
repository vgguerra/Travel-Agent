import os

import requests
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def get_lat_long(cidade):
    geolocator = Nominatim(user_agent="geoapi_exemplo")
    try:
        location = geolocator.geocode(cidade, timeout=10)
        if location:
            return location.latitude, location.longitude
        else:
            return None
    except Exception as e:
        print(f"Erro ao buscar coordenadas: {e}")
        return None

latitude,longitude = get_lat_long("São Paulo, Brasil")

url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotelsByCoordinates"


querystring = {"latitude":latitude,"longitude":longitude,"arrival_date":"2025-09-24","departure_date":"2025-09-28","adults":"1","children_age":"0,17","room_qty":"1","units":"metric","page_number":"1","temperature_unit":"c","languagecode":"pt-br","currency_code":"BRL","location":"BR"}


headers = {
	"x-rapidapi-key": os.getenv("RAPID_KEY"),
    "x-rapidapi-host": os.getenv("RAPID_HOST")
}


response = requests.get(url, headers=headers, params=querystring)
data = response.json()

hotels = data["data"]["result"]

for i, hotel in enumerate(hotels, 0):
    print(f"{i}. {hotel["hotel_name"]} - {hotel["composite_price_breakdown"]["net_amount"]["value"]} BRL")


# builder.set_entry_point("tourism_agent")
# builder.add_conditional_edges("tourism_agent", tools_condition)
# builder.add_edge("tools", "tourism_agent")

# builder.set_entry_point("transport_agent")
# builder.add_conditional_edges("transport_agent", tools_condition)
# builder.add_edge("tools", "transport_agent")

# builder.set_entry_point("accomodation_agent")
# builder.add_conditional_edges("accomodation_agent", tools_condition)
# builder.add_edge("tools","accomodation_agent") # builder.set_entry_point("weather_agent")

# builder.add_conditional_edges("weather_agent", tools_condition)
# builder.add_edge("tools", "weather_agent")