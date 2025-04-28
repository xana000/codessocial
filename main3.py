import os
from dotenv import load_dotenv
import groq
import fitz  # PyMuPDF
from collections import Counter

# --- Fonctions ---

def load_config():
    """"""Charge la clé API et le nom du fichier PDF depuis .env.""""""
    load_dotenv()
    api_key = os.getenv(""GROQ_API_KEY"")
    pdf_filename = os.getenv(""PDF_FILENAME"")

    if not api_key:
        raise ValueError("La clé API GROQ_API_KEY n'est pas définie dans le fichier .env.")
    if not pdf_filename:
        raise ValueError("Le nom du fichier PDF PDF_FILENAME n'est pas défini dans le fichier .env.")
    
    return api_key, pdf_filename

def initialize_groq_client(api_key):
    """"""Initialise le client Groq.""""""
    return groq.Groq(api_key=api_key)

def extract_text_from_pdf(pdf_path):
    "Extrait le texte brut d'un PDF."
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    if not text.strip():
        raise Exception(""Le PDF est vide ou non lisible."")
    return text

def split_text(text, max_chunk_size=12000):
    """"""Découpe le texte pour éviter de dépasser la limite de tokens.""""""
    return [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]

def detect_themes(client, model_name, text_chunk):
    """"""Demande à Groq d'identifier les thématiques sociologiques dans un extrait.""""""
    prompt = (
        ""Voici un entretien sociologique extrait d'un fichier PDF.\n""
        ""Identifie clairement les grandes thématiques sociologiques abordées dans ce texte :\n\n""
        + text_chunk
    )
    print(f""\n--- Modèle utilisé : {model_name} ---"")
    print(f""--- Prompt envoyé (extrait) ---\n{prompt[:500]}...\n"")
    response = client.chat.completions.create(
        model=model_name,
        messages=[{""role"": ""user"", ""content"": prompt}]
    )
    return response.choices[0].message.content

def parse_themes(themes_text):
    """"""Transforme la réponse Groq en liste de thématiques.""""""
    lines = themes_text.strip().split(""\n"")
    themes = []
    for line in lines:
        line = line.strip(""-•1234567890. "").strip()
        if line:
            themes.append(line.lower())
    return themes

def save_themes_to_file(themes, output_path):
    """"""Sauvegarde une liste de thématiques dans un fichier .txt.""""""
    with open(output_path, ""w"", encoding=""utf-8"") as f:
        for theme in themes:
            f.write(f""{theme}\n"")

def process_pdf(pdf_path, client, model_name, output_directory, file_name):
    """"""Traite un PDF pour extraire et sauvegarder les thématiques.""""""
    text = extract_text_from_pdf(pdf_path)
    chunks = split_text(text)

    all_themes = []

    for idx, chunk in enumerate(chunks):
        print(f""\n--- Résultat pour le morceau {idx+1}/{len(chunks)} ---\n"")
        themes_text = detect_themes(client, model_name, chunk)
        themes_list = parse_themes(themes_text)
        all_themes.extend(themes_list)

    output_path = os.path.join(output_directory, f""{file_name}_themes.txt"")
    save_themes_to_file(all_themes, output_path)

    print(f""\nThématiques sauvegardées dans {output_path}"")

# --- Programme principal ---

def main():
    api_key, pdf_filename = load_config()
    client = initialize_groq_client(api_key)
    model_name = ""gemma2-9b-it""

    file_name = os.path.splitext(pdf_filename)[0]  # Nom sans extension
    output_directory = ""./output""
    pdf_path = os.path.join(""./data"", pdf_filename)

    os.makedirs(output_directory, exist_ok=True)

    process_pdf(pdf_path, client, model_name, output_directory, file_name)

if __name__ == ""__main__"":
    main()"