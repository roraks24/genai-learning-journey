from decimal import Decimal, InvalidOperation
import requests, os


def calculator(expression: str) -> str:
    if not isinstance(expression, str):
        return "Error: expression must be a string."

    if not expression.strip():
        return "Error: expression cannot be empty."

    try:
        result = eval(expression)
        return str(result)

    except Exception as e:
        return f"Calculation error: {e}"


def get_weather(city: str) -> str:
    if not isinstance(city, str):
        return "Error: city must be a string."

    city = city.strip()

    if not city:
        return "Error: city cannot be empty."

    # ---------------------------------------------------------
    #           Convert city name -> latitude/longitude
    # ---------------------------------------------------------

    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

    geocoding_params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    try:
        response = requests.get(
            geocoding_url,
            params=geocoding_params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results", [])

        if not results:
            return f"Error: city not found: {city}"

        city_data = results[0]

        latitude = city_data.get("latitude")
        longitude = city_data.get("longitude")
        resolved_city = city_data.get("name", city)
        country = city_data.get("country", "Unknown")

        if latitude is None or longitude is None:
            return "Error: location coordinates were not available."

    except requests.RequestException as e:
        return f"Geocoding API request failed: {e}"

    except ValueError:
        return "Geocoding API returned invalid JSON."

    # ---------------------------------------------------------
    #         Get current weather using coordinates
    # ---------------------------------------------------------

    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "wind_speed_10m,"
            "weather_code"
        ),
        "timezone": "auto"
    }

    try:
        response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        current = data.get("current", {})
        units = data.get("current_units", {})

        if not current:
            return "Error: current weather data was unavailable."

        temperature = current.get("temperature_2m", "Unknown")
        humidity = current.get("relative_humidity_2m", "Unknown")
        apparent_temperature = current.get(
            "apparent_temperature",
            "Unknown"
        )
        wind_speed = current.get(
            "wind_speed_10m",
            "Unknown"
        )
        weather_code = current.get(
            "weather_code",
            "Unknown"
        )

        temperature_unit = units.get(
            "temperature_2m",
            "°C"
        )
        wind_unit = units.get(
            "wind_speed_10m",
            "km/h"
        )

        return (
            f"City: {resolved_city}, {country}\n"
            f"Temperature: {temperature} {temperature_unit}\n"
            f"Feels Like: {apparent_temperature} {temperature_unit}\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_speed} {wind_unit}\n"
            f"Weather Code: {weather_code}"
        )

    except requests.RequestException as e:
        return f"Weather API request failed: {e}"

    except ValueError:
        return "Weather API returned invalid JSON."


def get_country_info(country: str) -> str:


    if not isinstance(country, str):
        return "Error: country must be a string."

    country = country.strip()

    if not country:
        return "Error: country cannot be empty."

    url = (
        "https://api.restcountries.com/"
        f"countries/v5/names.common/{country}"
    )

    headers = {
        "Authorization": "Bearer rc_live_demo"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        countries = data.get(
            "data", {}
        ).get(
            "objects", []
        )

        if not countries:
            return f"Error: country not found: {country}"

        country_data = countries[0]

        name = country_data.get(
            "names", {}
        ).get(
            "common",
            country
        )

        capitals = country_data.get(
            "capitals",
            []
        )

        capital = (
            capitals[0].get("name", "Unknown")
            if capitals
            else "Unknown"
        )

        region = country_data.get(
            "region",
            "Unknown"
        )

        population = country_data.get(
            "population",
            "Unknown"
        )

        return (
            f"Country: {name}\n"
            f"Capital: {capital}\n"
            f"Region: {region}\n"
            f"Population: {population}"
        )

    except requests.RequestException as e:
        return f"API request failed: {e}"

    except ValueError:
        return "API returned invalid JSON"



def currency_converter(
    amount: float,
    from_currency: str,
    to_currency: str
) -> str:

    # -----------------------------
    # Validate amount
    # -----------------------------

    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, ValueError, TypeError):
        return "Error: amount must be a valid number."

    if amount <= 0:
        return "Error: amount must be greater than 0."

    # -----------------------------
    # Validate currency codes
    # -----------------------------

    if not isinstance(from_currency, str):
        return "Error: from_currency must be a string."

    if not isinstance(to_currency, str):
        return "Error: to_currency must be a string."

    from_currency = from_currency.strip().upper()
    to_currency = to_currency.strip().upper()

    if len(from_currency) != 3:
        return "Error: from_currency must be a 3-letter currency code."

    if len(to_currency) != 3:
        return "Error: to_currency must be a 3-letter currency code."

    # Same-currency conversion
    if from_currency == to_currency:
        return (
            f"{amount} {from_currency} = "
            f"{amount} {to_currency}"
        )

    # -----------------------------
    # Get exchange rate
    # -----------------------------

    url = (
        f"https://api.frankfurter.dev/v2/"
        f"rate/{from_currency}/{to_currency}"
    )

    try:
        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        rate = data.get("rate")

        if rate is None:
            return "Error: exchange rate was not returned by the API."

        rate = Decimal(str(rate))

        # -----------------------------
        # Calculate converted amount
        # -----------------------------

        converted_amount = amount * rate

        return (
            f"{amount} {from_currency} = "
            f"{converted_amount:.2f} {to_currency}\n"
            f"Exchange rate: 1 {from_currency} = "
            f"{rate} {to_currency}\n"
            f"Rate date: {data.get('date', 'Unknown')}"
        )

    except requests.RequestException as e:
        return f"Currency API request failed: {e}"

    except ValueError:
        return "Currency API returned invalid JSON."

    except InvalidOperation:
        return "Error: invalid exchange rate returned by the API."


def web_search(query: str) -> str:

    if not isinstance(query, str):
        return "Error: query must be a string."

    query = query.strip()

    if not query:
        return "Error: query cannot be empty."

    api_key = os.getenv("FREESEA_API_KEY")

    if not api_key:
        return "Error: FREESEA_API_KEY is not configured."

    url = "https://freesea.dev/v1/search"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": query,
        "num_results": 5,
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results", [])

        if not results:
            return f"No search results found for: {query}"

        formatted_results = []

        for index, result in enumerate(results, start=1):
            title = result.get("title", "Untitled")
            url = result.get("url", "")
            snippet = result.get(
                "content",
                result.get("snippet", "")
            )

            formatted_results.append(
                f"{index}. {title}\n"
                f"URL: {url}\n"
                f"Snippet: {snippet}"
            )

        return "\n\n".join(formatted_results)

    except requests.RequestException as e:
        return f"Web search API request failed: {e}"

    except ValueError:
        return "Web search API returned invalid JSON."

def get_datetime(location_or_timezone: str) -> str:
    if not isinstance(location_or_timezone, str):
        return "Error: location_or_timezone must be a string."

    location_or_timezone = location_or_timezone.strip()

    # Use India as the default when no location is provided.
    if not location_or_timezone:
        location_or_timezone = "Asia/Kolkata"

    # Simple location -> timezone mapping for the mini-agent.
    # We can expand this later if needed.
    timezone_map = {
        "india": "Asia/Kolkata",
        "jaipur": "Asia/Kolkata",
        "delhi": "Asia/Kolkata",
        "mumbai": "Asia/Kolkata",
        "tokyo": "Asia/Tokyo",
        "london": "Europe/London",
        "new york": "America/New_York",
        "singapore": "Asia/Singapore",
    }

    timezone = timezone_map.get(
        location_or_timezone.lower(),
        location_or_timezone
    )

    url = f"https://timeapi.io/api/Time/current/zone?timeZone={timezone}"

    try:
        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        date = data.get("date")
        time = data.get("time")
        day_of_week = data.get("dayOfWeek")
        time_zone = data.get("timeZone")

        if not date or not time:
            return "Error: current date/time was not returned by the API."

        return (
            f"Timezone: {time_zone or timezone}\n"
            f"Date: {date}\n"
            f"Time: {time}\n"
            f"Day: {day_of_week or 'Unknown'}"
        )

    except requests.Timeout:
        return "Date/time API request timed out."

    except requests.RequestException as e:
        return f"Date/time API request failed: {e}"

    except ValueError:
        return "Date/time API returned invalid JSON."