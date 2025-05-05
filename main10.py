import os
import re
from dotenv import load_dotenv
from groq import Groq
from PyPDF2 import PdfReader

def load_api_key():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("La clé API Groq n'est pas définie.")
    return api_key

def extract_samples_from_pdfs(directory, max_characters_per_pdf=1000):
    pdf_samples = {}
    pdf_files = sorted([f for f in os.listdir(directory) if f.endswith('.pdf')])
    for pdf_file in pdf_files:
        reader = PdfReader(os.path.join(directory, pdf_file))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        dialogue_matches = re.findall(r'「.*?」|“.*?”|‘.*?’', text, re.DOTALL)
        if dialogue_matches:
            sample = " ".join(dialogue_matches)[:max_characters_per_pdf].strip()
        else:
            sample = text[:max_characters_per_pdf].strip()
        pdf_samples[pdf_file] = sample
    return pdf_samples

def extract_themes(api_key, pdf_samples, label):
    client = Groq(api_key=api_key)
    combined_text = ""
    for pdf_file, sample in pdf_samples.items():
        combined_text += f"\n--- {label}: {pdf_file} ---\n{sample}\n"

    prompt = (
        f"Voici les extraits des entretiens du dossier {label}.\n"
        " partir de ce texte, identifie les thématiques intéressantes pour une analyse sociologique entre Data1 et Data2, et pour chaque thème sociologique, identifie des sous-thèmes pertinents. et pour chaque sous-thème, donne moi toutes les verbatims associées à ces thèmes :\n\n "
        f"{combined_text}"
    )

    response = client.chat.completions.create(
        model="mistral-saba-24b",
        messages=[{"role": "system", "content": prompt}],
    )
    return response.choices[0].message.content

def extract_common_themes(api_key, data1_themes, data2_themes):
    client = Groq(api_key=api_key)
    prompt = (
        "Voici les thèmes et les citations extraits de deux ensembles de données :\n\n"
        f"Data1:\n{data1_themes}\n\n"
        f"Data2:\n{data2_themes}\n\n"
        "Identifie les thèmes communs entre Data1 et Data2. "
        "Identifie au moins dix codes sociologiques pertinents, même s'ils sont moins fréquents."
        "Pour chaque thème commun, donne au moins une citation de Data1 et une citation de Data2."
    )
    response = client.chat.completions.create(
        model="mistral-saba-24b",
        messages=[{"role": "system", "content": prompt}],
    )
    return response.choices[0].message.content

def save_output_to_file(content, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    api_key = load_api_key()

    # Data1の処理
    data1_samples = extract_samples_from_pdfs('data1/')
    print("✅ Data1 分析中...")
    data1_themes = extract_themes(api_key, data1_samples, "Data1")

    # Data2の処理
    data2_samples = extract_samples_from_pdfs('data2/')
    print("✅ Data2 分析中...")
    data2_themes = extract_themes(api_key, data2_samples, "Data2")

    # 共通テーマ抽出
    print("✅ 共通テーマ抽出中...")
    common_themes = extract_common_themes(api_key, data1_themes, data2_themes)

    # ファイル保存
    save_output_to_file(data1_themes, './output/data1_themes.txt')
    save_output_to_file(data2_themes, './output/data2_themes.txt')
    save_output_to_file(common_themes, './output/common_themes.txt')

    # ターミナル出力
    print("\n✅ 共通テーマと引用（Data1, Data2）:")
    print(common_themes)

if __name__ == '__main__':
    main()
