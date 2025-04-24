import os
import re
import math
import pymorphy2
from bs4 import BeautifulSoup
from collections import defaultdict, Counter

# Настройки
INPUT_DIR = "downloaded_pages"
TFIDF_TOKENS_PREFIX = "tfidf_tokens_"
TFIDF_LEMMAS_PREFIX = "tfidf_lemmas_"

OUTPUT_DIR = "tf_idf"

IGNORED_POS = {"CONJ", "PREP", "NUMB"}

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Инициализация лемматизатора
morph = pymorphy2.MorphAnalyzer()


def extract_tokens(text):
    # Токенизация текста: извлечение слов без союзов, предлогов и чисел
    words = re.findall(r"[а-яА-ЯёЁ]+", text.lower())
    return [word for word in words if morph.parse(word)[0].tag.POS not in IGNORED_POS]


def compute_idf(documents):
    n = len(documents)
    df = defaultdict(int)
    for doc in documents:
        for term in set(doc):
            df[term] += 1
    idf = {term: math.log(n / df[term]) for term in df}
    return idf


def compute_tf(doc):
    total = len(doc)
    tf = Counter(doc)
    return {term: tf[term] / total for term in tf}


def write_tfidf_file(filename, tf, idf, out_prefix):
    filepath = os.path.join(OUTPUT_DIR, out_prefix + filename + '.txt')
    with open(filepath, "w", encoding="utf-8") as f:
        for term in sorted(tf):
            tfidf = tf[term] * idf.get(term, 0)
            f.write(f"{term} {idf.get(term, 0):.6f} {tfidf:.6f}\n")


def lemmatize_doc(doc):
    lemma_doc = []
    for word in doc:
        lemma = morph.parse(word)[0].normal_form
        lemma_doc.append(lemma)
    return lemma_doc


# Основной процесс
all_docs_tokens = []
all_docs_lemmas = []
filenames = []

for filename in os.listdir(INPUT_DIR):
    filepath = os.path.join(INPUT_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        content = content.replace(">", "> ")
        content = content.replace("<", " <")

        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text()
        tokens = extract_tokens(text)
        lemmas = lemmatize_doc(tokens)

        all_docs_tokens.append(tokens)
        all_docs_lemmas.append(lemmas)
        filenames.append(filename)

# IDF по всем документам
idf_tokens = compute_idf(all_docs_tokens)
idf_lemmas = compute_idf(all_docs_lemmas)

# TF и TF-IDF по каждому документу
for i in range(len(filenames)):
    filename = filenames[i]
    tf_tokens = compute_tf(all_docs_tokens[i])
    tf_lemmas = compute_tf(all_docs_lemmas[i])

    write_tfidf_file(filename, tf_tokens, idf_tokens, TFIDF_TOKENS_PREFIX)
    write_tfidf_file(filename, tf_lemmas, idf_lemmas, TFIDF_LEMMAS_PREFIX)

print("TF-IDF по токенам и леммам успешно рассчитаны и записаны в файлы.")
