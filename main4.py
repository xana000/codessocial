import os
from dotenv import load_dotenv
from groq import Groq
from PyPDF2 import PdfReader

# Charger les variables d'environnement
def load_api_key():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("La clé API Groq n'est pas définie.")
    return api_key

# Lire et limiter le contenu du PDF à une taille raisonnable
def extract_text_from_pdf(pdf_path, max_characters=5000):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
        if len(text) >= max_characters:
            break
    return text[:max_characters]

# Identifier les thématiques principales avec Groq
def extract_themes(api_key, text):
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "Tu es un assistant sociologique. Tu dois classer les thématiques de l'entretien selon des catégories sociologiques pertinentes (par exemple : identité, pouvoir, culture, travail, genre, etc.)."},
            {"role": "user", "content": f"Analyse sociologiquement le texte suivant et regroupe les principales thématiques en catégories sociologiques pertinentes :\n\n{text}"}
        ],
    )

    return response.choices[0].message.content

# Fonction principale
def main():
    api_key = load_api_key()
    pdf_path = './data/KanakoINOUE.pdf'  # Adapter au nom réel de ton fichier

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Le fichier {pdf_path} n'existe pas.")

    pdf_text = extract_text_from_pdf(pdf_path)
    themes = extract_themes(api_key, pdf_text)

    print("Thématiques principales de l'entretien :")
    print(themes)

# Exécution du script
if __name__ == '__main__':
    main()
