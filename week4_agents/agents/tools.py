def calculator(expression:str):
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Calculation error: {e}"


def get_weather(city:str) -> str:
    return f"The weather of {city} is sunny"


    