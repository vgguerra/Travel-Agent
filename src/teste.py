from amadeus import Client, ResponseError
from dotenv import load_dotenv

load_dotenv()
amadeus = Client()

try:

    from amadeus import Location

    response = amadeus.reference_data.locations.hotels.by_city.get(cityCode='PAR')

    print(response.body)  # => The raw response, as a string
    print(response.result)  # => The body parsed as JSON, if the result was parsable
    print(response.data)  # => The list of locations, extracted from the JSON
except ResponseError as error:
    print(error)

