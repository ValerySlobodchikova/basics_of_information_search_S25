import os
import re
import pymorphy2
from bs4 import BeautifulSoup
from collections import defaultdict

INPUT_DIR = "downloaded_pages"
OUTPUT_DIR = "lemmas_and_tokens"

IGNORED_POS = {"CONJ", "PREP", "NUMB"}

# Инициализация лемматизатора
morph = pymorphy2.MorphAnalyzer()

os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_tokens(text):
    # Токенизация текста: извлечение слов без союзов, предлогов и чисел
    words = re.findall(r"[а-яА-ЯёЁ]+", text.lower())
    return [word for word in words if morph.parse(word)[0].tag.POS not in IGNORED_POS]


# Читаем файлы и извлекаем токены

for filename in os.listdir(INPUT_DIR):
    tokens = set()
    filepath = os.path.join(INPUT_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

        # Добавляем пробелы до и после html тегов, чтобы слова после soup.get_text() не слипались
        content = content.replace(">", "> ")
        content = content.replace("<", " <")

        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text()
        tokens.update(extract_tokens(text))

    # Записываем токены в файл
    with open(os.path.join(OUTPUT_DIR, f"tokens_{filename}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(tokens)))

    # Лемматизация и группировка
    lemmas = defaultdict(set)
    for token in tokens:
        lemma = morph.parse(token)[0].normal_form
        lemmas[lemma].add(token)

    # Записываем леммы в файл
    with open(os.path.join(OUTPUT_DIR, f"lemmas_{filename}.txt"), "w", encoding="utf-8") as f:
        for lemma, words in lemmas.items():
            f.write(f"{lemma} {' '.join(words)}\n")
