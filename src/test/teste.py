import requests
from geopy.geocoders import Nominatim

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

url = "https://booking-com.p.rapidapi.com/v2/hotels/search-by-coordinates"

querystring = {"include_adjacency":"true","children_ages":"5,0","categories_filter_ids":"class::2,class::4,free_cancellation::1","page_number":"0","children_number":"2","adults_number":"2","checkout_date":"2025-10-15","longitude":longitude,"room_number":"1","order_by":"popularity","units":"metric","checkin_date":"2025-10-14","latitude":latitude,"filter_by_currency":"BRL","locale":"pt-br"}

headers = {
	"x-rapidapi-key": "eb506d7ea4msh0f24bd3860a9d4bp148edcjsn7690c17937b1",
	"x-rapidapi-host": "booking-com.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)
data = response.json()

hotels = data.get("results", [])[:10]

for i, hotel in enumerate(hotels, 1):
    print(f"{i}. {hotel["name"]} - {hotel.get('address')} - {hotel["priceBreakdown"]["grossPrice"]["value"]} BRL")