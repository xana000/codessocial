import os
import re
from collections import Counter
from pathlib import Path
from dotenv import load_dotenv
import groq

# === Charger la clé API depuis .env ===

load_dotenv()  # Charge le fichier .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("La clé API GROQ_API_KEY n'est pas définie dans le fichier .env.")

LLAMA_MODEL = "llama3-70b-8192"

# === Paramètres ===

FOLDER_PATH = "output1"
GLOBAL_THEMES_FILE = "thèmes_globaux.txt"
TOP_10_FILE = "top_10.txt"

# === 1. Extraction des thèmes ===

all_themes = []

for filename in os.listdir(FOLDER_PATH):
    if filename.endswith(".txt"):
        with open(os.path.join(FOLDER_PATH, filename), "r", encoding="utf-8") as f:
            content = f.read()
            themes = re.findall(r"\*\*\s*(.*?)\s*\*\*", content)
            all_themes.extend(themes)

# === 2. Sauvegarder tous les thèmes ===

with open(GLOBAL_THEMES_FILE, "w", encoding="utf-8") as f:
    for theme in all_themes:
        f.write(theme + "\n")

print(f"[OK] Tous les thèmes ont été sauvegardés dans '{GLOBAL_THEMES_FILE}'.")

# === 3. Calcul du top 10 ===

theme_counts = Counter(all_themes)
top_10 = theme_counts.most_common(10)

with open(TOP_10_FILE, "w", encoding="utf-8") as f:
    for theme, count in top_10:
        f.write(f"{theme} ({count} occurrences)\n")

print(f"[OK] Le top 10 des thèmes a été sauvegardé dans '{TOP_10_FILE}'.")

# === 4. Proposer une manière d’analyser ces thèmes avec Llama 4 ===

client = groq.Groq(api_key=GROQ_API_KEY)

prompt = f"""
Voici une liste de thèmes issus d'entretiens sociologiques :

{chr(10).join(set(all_themes))}

Propose une méthode rigoureuse et détaillée pour analyser ces thèmes sociologiquement (par exemple : classification, mise en relation, comparaison entre entretiens...). Ta réponse doit être structurée et précise, adaptée à un travail de recherche.
"""

chat_completion = client.chat.completions.create(
    model=LLAMA_MODEL,
    messages=[
        {"role": "system", "content": "Tu es un expert en analyse sociologique."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7
)

result = chat_completion.choices[0].message.content

# Sauvegarder la proposition de méthode d'analyse
with open("proposition_analyse_llama.txt", "w", encoding="utf-8") as f:
    f.write(result)

print("[OK] Proposition d'analyse enregistrée dans 'proposition_analyse_llama.txt'.")
