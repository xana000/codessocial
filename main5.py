import os
from dotenv import load_dotenv
from groq import Groq
from PyPDF2 import PdfReader

# 環境変数を読み込む
def load_api_key():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("La clé API Groq n'est pas définie.")
    return api_key

# 複数PDFからテキストを結合する
def extract_texts_from_pdfs(directory, max_characters=5000):
    combined_text = ""
    pdf_files = sorted([f for f in os.listdir(directory) if f.endswith('.pdf')])
    for pdf_file in pdf_files:
        reader = PdfReader(os.path.join(directory, pdf_file))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                combined_text += page_text
    # 最後にまとめてカットする
    return combined_text[:max_characters]

# Groqでテーマを抽出
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

# 結果をファイルに保存
def save_output_to_file(content, output_path='./output/themes_output.txt'):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

# メイン関数
def main():
    api_key = load_api_key()
    pdf_directory = './data/'

    if not os.path.exists(pdf_directory):
        raise FileNotFoundError(f"Le dossier {pdf_directory} n'existe pas.")

    combined_text = extract_texts_from_pdfs(pdf_directory)
    themes = extract_themes(api_key, combined_text)

    # ターミナルに表示
    print("Thématiques principales des entretiens combinés :")
    print(themes)

    # ファイルに保存
    output_path = './output/themes_output.txt'
    save_output_to_file(themes, output_path)
    print(f"✅ Résultats enregistrés dans : {output_path}")

# 実行
if __name__ == '__main__':
    main()
