import requests


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

    return f"The weather of {city} is sunny"


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


if __name__ == "__main__":

    print("--- Calculator ---")
    print(calculator("25 * 17"))

    print("\n--- Weather ---")
    print(get_weather("Jaipur"))

    print("\n--- Country ---")
    print(get_country_info("India"))

    print("\n--- Empty country ---")
    print(get_country_info(""))

    print("\n--- Wrong type ---")
    print(get_country_info(123))