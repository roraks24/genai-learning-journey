from dotenv import load_dotenv
from groq import Groq


load_dotenv()


client = Groq()

models = client.models.list()


for model in models.data:

    if model.active:
        print(model.id)