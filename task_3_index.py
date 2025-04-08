import os
import json
from collections import defaultdict

INPUT_DIR = "./lemmas_and_tokens"


def extract_doc_id(filename):
    return filename.replace("lemmas_", "").replace(".txt", "")


def load_all_lemmas(folder_path):
    lemma_files = sorted(
        [f for f in os.listdir(folder_path) if f.startswith("lemmas_") and f.endswith(".txt")]
    )
    documents = []
    doc_ids = []
    for filename in lemma_files:
        with open(os.path.join(folder_path, filename), encoding='utf-8') as f:
            lemmas = f.read().strip().split()
            documents.append(lemmas)
            doc_ids.append(extract_doc_id(filename))
    return documents, doc_ids


def build_inverted_index(docs, doc_ids):
    index = defaultdict(set)
    for lemmas, doc_id in zip(docs, doc_ids):
        for lemma in lemmas:
            index[lemma.lower()].add(doc_id)
    return {term: sorted(list(postings)) for term, postings in index.items()}


def save_index(index, path='inverted_index.json'):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    docs, doc_ids = load_all_lemmas(INPUT_DIR)
    index = build_inverted_index(docs, doc_ids)
    save_index(index)
    print(f"Индекс по леммам сохранён в 'inverted_index.json' с {len(index)} терминами.")
