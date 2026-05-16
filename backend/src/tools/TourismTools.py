import requests
from langchain_core.tools import tool

from src.config import settings


def get_geocode(city: str):
    url = "https://tripadvisor-com1.p.rapidapi.com/auto-complete"

    query_string = {"query": city}

    headers = {
        "x-rapidapi-key": settings.RAPID_KEY,
        "x-rapidapi-host": "tripadvisor-com1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=query_string)

    return response.json()["data"][0]["geoId"]

class TourismTools:



    @staticmethod
    @tool(name_or_callable="getTourismIdeas",description="Provides a list of recommended tourism activities, attractions, and experiences for a given city and date range, optionally tailored to traveler preferences."
    )
    def getTourismIdeas( city: str, startDate: str, endDate: str, adults: int):
        """
            Generate tourism activity suggestions for a specific city within a given date range.

            This function provides curated ideas for sightseeing, cultural experiences,
            and local attractions based on the destination city, travel dates, and number of travelers.

            Args:
                city (str): Name of the city to explore (e.g., "Paris").
                startDate (str): Start date of the trip in "YYYY-MM-DD" format.
                endDate (str): End date of the trip in "YYYY-MM-DD" format.
                adults (int): Number of adult travelers.

            Returns:
                list[dict]: A list of suggested activities, where each item contains details such as:
                            - day (int): The day of the itinerary.
                            - activity (str): Description of the activity or attraction.
                            - optional details like location, duration, or category.
        """

        url = "https://tripadvisor-com1.p.rapidapi.com/attractions/search"

        headers = {
            "x-rapidapi-key": settings.RAPID_KEY,
            "x-rapidapi-host": "tripadvisor-com1.p.rapidapi.com"
        }

        geo_code = get_geocode(city)

        querystring = {"geoId": geo_code, "startDate": startDate, "endDate": endDate, "units": "kilometers",
                       "sortType": "asc", "adults": str(adults), }

        attractions = requests.get(url, headers=headers, params=querystring).json()["data"]["attractions"]

        results = []

        for i, attraction in enumerate(attractions,start=1):
            # print(f"{attraction["cardTitle"]["string"]} - INFO: {attraction["primaryInfo"]["text"]}")

            results.append({
                "index": i,
                "atraction_name": attraction["cardTitle"]["string"],
                "atraction_info": attraction["primaryInfo"]["text"]
            })

        return results


if __name__ == "__main__":
    tool = TourismTools()

    tool.getTourismIdeas("Florianopolis","2025-10-08","2025-10-10",1)