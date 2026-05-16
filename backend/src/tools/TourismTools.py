import requests
from langchain_core.tools import tool

from src.config import settings

HOST = "tripadvisor-com1.p.rapidapi.com"
AUTOCOMPLETE_URL = f"https://{HOST}/auto-complete"
ATTRACTIONS_URL = f"https://{HOST}/attractions/search"


def _headers() -> dict[str, str]:
    return {
        "x-rapidapi-key": settings.RAPID_KEY,
        "x-rapidapi-host": HOST,
    }


def _get_geo_id(city: str) -> int | None:
    try:
        response = requests.get(AUTOCOMPLETE_URL, headers=_headers(),
                                params={"query": city}, timeout=10)
        response.raise_for_status()
        payload = response.json() or {}
        items = payload.get("data") or []
        for item in items:
            geo_id = item.get("geoId")
            if geo_id:
                return geo_id
    except requests.exceptions.RequestException:
        return None
    return None


class TourismTools:

    @staticmethod
    @tool(
        name_or_callable="getTourismIdeas",
        description="Provides a list of recommended tourism activities, attractions, and experiences for a given city and date range, optionally tailored to traveler preferences."
    )
    def getTourismIdeas(city: str, startDate: str, endDate: str, adults: int):
        """
        Generate tourism activity suggestions for a specific city within a given date range.

        Args:
            city (str): Name of the city to explore (e.g., "Paris").
            startDate (str): Start date of the trip in "YYYY-MM-DD" format.
            endDate (str): End date of the trip in "YYYY-MM-DD" format.
            adults (int): Number of adult travelers.

        Returns:
            list[dict] or str: A list of suggested attractions on success, or an
            error message string on failure.
        """
        geo_id = _get_geo_id(city)
        if geo_id is None:
            return f"Não foi possível encontrar a cidade '{city}' na base de turismo."

        querystring = {
            "geoId": geo_id,
            "startDate": startDate,
            "endDate": endDate,
            "units": "kilometers",
            "sortType": "asc",
            "adults": str(adults),
        }

        try:
            response = requests.get(ATTRACTIONS_URL, headers=_headers(),
                                    params=querystring, timeout=15)
            response.raise_for_status()
            payload = response.json() or {}
        except requests.exceptions.Timeout:
            return "A busca de atrações excedeu o tempo limite. Tente novamente mais tarde."
        except requests.exceptions.RequestException:
            return "Erro ao buscar atrações: serviço temporariamente indisponível."
        except ValueError:
            return "Erro ao processar a resposta de turismo."

        data = payload.get("data")
        if not isinstance(data, dict):
            return "Nenhuma atração encontrada para os critérios informados."

        attractions = data.get("attractions") or []
        if not attractions:
            return "Nenhuma atração encontrada para os critérios informados."

        results = []
        for i, attraction in enumerate(attractions[:30], start=1):
            name = (attraction.get("cardTitle") or {}).get("string")
            info = (attraction.get("primaryInfo") or {}).get("text")
            if not name:
                continue
            results.append({
                "index": i,
                "atraction_name": name,
                "atraction_info": info or "",
            })

        if not results:
            return "Nenhuma atração com nome disponível para esse destino."
        return results
