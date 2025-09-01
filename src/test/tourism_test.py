import os
from dotenv import load_dotenv
import requests

load_dotenv()

url = "https://tripadvisor-com1.p.rapidapi.com/attractions/search"

querystring = {"geoId":"303576","startDate":"2025-09-16","endDate":"2025-09-18","units":"miles","sortType":"asc"}

headers = {
	"x-rapidapi-key": os.getenv("RAPID_KEY"),
	"x-rapidapi-host": "tripadvisor-com1.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring).json()

print(response)