from langchain_core.tools import tool

class AccomodationTools:

    def __init__(self):
        pass

    @staticmethod
    @tool(name_or_callable="getAccomodation", description="Get accomodation options at the specified days and city")
    def getAccomodation(city: str, checkin: str, checkout: str, type_: str) :
        """
            Função que simula a busca de acomodações.
            Retorna uma lista de opções.
            """
        results = [
            {"name": "Hotel A", "price": 120, "rating": 4.5},
            {"name": "Hostel B", "price": 50, "rating": 4.0},
            {"name": "Hotel C", "price": 200, "rating": 5.0},
        ]
        # Filtra pelo tipo se necessário
        return [r for r in results if type_.lower() in r["name"].lower()]