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

# Lire le contenu du PDF
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Faire une requête à Groq
def summarize_text(api_key, text):
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[
            {"role": "system", "content": "Tu es un assistant chargé de résumer précisément les textes."},
            {"role": "user", "content": f"Résume le texte suivant :\n\n{text}"}
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
    summary = summarize_text(api_key, pdf_text)

    print("Résumé du document :")
    print(summary)

# Exécution du script
if __name__ == '__main__':
    main()
