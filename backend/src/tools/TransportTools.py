from datetime import datetime

import requests
from langchain_core.tools import tool

from src.config import settings

HOST = "booking-com15.p.rapidapi.com"
SEARCH_URL = f"https://{HOST}/api/v1/flights/searchFlights"
LOOKUP_URL = f"https://{HOST}/api/v1/flights/searchDestination"


def _headers() -> dict[str, str]:
    return {
        "x-rapidapi-key": settings.RAPID_KEY,
        "x-rapidapi-host": HOST,
    }


def _lookup_location_id(query: str) -> str | None:
    """Resolve a city name or IATA code into Booking's location id (e.g. GRU.AIRPORT)."""
    try:
        response = requests.get(LOOKUP_URL, headers=_headers(), params={"query": query}, timeout=10)
        response.raise_for_status()
        payload = response.json()
        if not payload.get("status"):
            return None
        items = payload.get("data") or []
        # Prefer airport entries to match IATA codes precisely
        for item in items:
            if item.get("type") == "AIRPORT" and item.get("code", "").upper() == query.upper():
                return item.get("id")
        for item in items:
            if item.get("type") == "AIRPORT":
                return item.get("id")
        if items:
            return items[0].get("id")
    except requests.exceptions.RequestException:
        return None
    return None


def _format_price(price: dict | None) -> str:
    if not price:
        return "preço não disponível"
    units = price.get("units", 0) or 0
    nanos = price.get("nanos", 0) or 0
    currency = price.get("currencyCode", "BRL")
    total = units + nanos / 1_000_000_000
    return f"{currency} {total:,.2f}"


def _seconds_to_hm(seconds: int | None) -> str:
    if not seconds:
        return ""
    hours, remainder = divmod(int(seconds), 3600)
    minutes = remainder // 60
    return f"{hours}h{minutes:02d}m"


def _summarize_offer(offer: dict, idx: int) -> dict:
    price_total = offer.get("priceBreakdown", {}).get("total", {})
    segments = offer.get("segments", []) or []
    summary = {
        "index": idx,
        "price": _format_price(price_total),
        "trip_type": offer.get("tripType"),
        "segments": [],
    }
    for seg in segments:
        legs = seg.get("legs", []) or []
        carriers = []
        stops = max(len(legs) - 1, 0)
        for leg in legs:
            for carrier in leg.get("carriersData", []) or []:
                name = carrier.get("name")
                if name and name not in carriers:
                    carriers.append(name)
        summary["segments"].append({
            "from": seg.get("departureAirport", {}).get("code"),
            "to": seg.get("arrivalAirport", {}).get("code"),
            "departure": seg.get("departureTime"),
            "arrival": seg.get("arrivalTime"),
            "duration": _seconds_to_hm(seg.get("totalTime")),
            "stops": stops,
            "carriers": carriers,
        })
    return summary


class TransportTools:

    @staticmethod
    @tool(
        name_or_callable="getFlights",
        description="Get flights at the specified days and city"
    )
    def getFlights(
            departure_city: str,
            arrival_city: str,
            date: str,
            itinerary_type: str,
            adults: int,
            num_senior: int = 0,
            return_date: str | None = None,
            class_type: str = "ECONOMY"
    ):
        """
        Search for flight options using the Booking.com Flights endpoint (RapidAPI).

        Args:
            departure_city: IATA code of the origin airport (e.g., 'GRU').
            arrival_city:   IATA code of the destination airport (e.g., 'CDG').
            date:           Departure date in 'YYYY-MM-DD'.
            itinerary_type: 'ONE_WAY' or 'ROUND_TRIP'.
            adults:         Number of adult passengers.
            num_senior:     Number of senior passengers. Unused by this endpoint.
            return_date:    Return date in 'YYYY-MM-DD' (required when ROUND_TRIP).
            class_type:     Cabin class (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST).

        Returns:
            list[dict] or str: list of flight summaries on success, or an error message.
        """
        allowed_classes = ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"]
        if class_type not in allowed_classes:
            return f"Erro: class_type inválido. Escolha entre: {', '.join(allowed_classes)}"

        def _is_valid_date(value: str) -> bool:
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return True
            except (ValueError, TypeError):
                return False

        if not _is_valid_date(date):
            return f"Erro: Data inválida: {date}. Use o formato YYYY-MM-DD."
        if return_date and not _is_valid_date(return_date):
            return f"Erro: Data de retorno inválida: {return_date}. Use o formato YYYY-MM-DD."

        from_id = _lookup_location_id(departure_city)
        if not from_id:
            return f"Não foi possível resolver a origem '{departure_city}'."
        to_id = _lookup_location_id(arrival_city)
        if not to_id:
            return f"Não foi possível resolver o destino '{arrival_city}'."

        querystring = {
            "fromId": from_id,
            "toId": to_id,
            "departDate": date,
            "adults": str(adults),
            "sort": "BEST",
            "cabinClass": class_type,
            "currency_code": "BRL",
        }
        if itinerary_type == "ROUND_TRIP":
            if not return_date:
                return "Erro: viagem ROUND_TRIP exige return_date."
            querystring["returnDate"] = return_date

        try:
            response = requests.get(SEARCH_URL, headers=_headers(), params=querystring, timeout=20)
            response.raise_for_status()
            data = response.json()

            if not data.get("status", True):
                msg = data.get("message") or "indisponível"
                return f"A API de voos retornou erro: {msg}"

            offers = (data.get("data") or {}).get("flightOffers") or []
            if not offers:
                return "Nenhum voo encontrado para os critérios informados."

            return [_summarize_offer(offer, i) for i, offer in enumerate(offers[:10], start=1)]

        except requests.exceptions.Timeout:
            return "A busca de voos excedeu o tempo limite. Tente novamente mais tarde."
        except requests.exceptions.RequestException:
            return "Erro ao buscar voos: serviço temporariamente indisponível."
        except Exception as exc:
            return f"Erro inesperado ao buscar voos: {exc}"
