import os
from dotenv import load_dotenv
from groq import Groq

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Récupérer la clé API Groq depuis les variables d'environnement
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("La clé API Groq n'est pas définie dans le fichier .env")

# Initialiser le client Groq
client = Groq(api_key=api_key)

# Faire une requête à Groq en utilisant Llama3-8b-8192 (adapter le modèle si Llama4 est disponible ultérieurement)
response = client.chat.completions.create(
    model="gemma2-9b-it",
    messages=[
        {"role": "system", "content": "Tu es un assistant utile et clair."},
        {"role": "user", "content": "Explique-moi brièvement ce qu'est Groq."}
    ],
)

# Afficher la réponse du modèle
print("Réponse de Groq:", response.choices[0].message.content)
