# task_5: берём запрос, лемматизируем, получаем вектор TF‑IDF
# -через инвертированный индекс быстро находим "кандидатные" документы (те, где встречается >=1 терм запроса)
# -считаем косинус только для "кандидатов"
# -выводим top‑k
# ---------------------------------------------------------------------------------
# -ЗАПУСК:  python task_5.py "россия экономика" [top_k]
# ---------------------------------------------------------------------------------

from __future__ import annotations
import json
import math
import os
import re
import sys
from collections import Counter
from typing import Dict, Set, List, Tuple

import pymorphy2

# настройки
TFIDF_DIR = "tf_idf"  # готовые веса
FILE_PREFIX = "tfidf_lemmas_"  # веса по леммам
INVERTED_INDEX_FILE = "inverted_index.json"
IGNORED_POS = {"CONJ", "PREP", "NUMB"}

_morph = pymorphy2.MorphAnalyzer()


# загрузка готовых TF‑IDF‑векторов документов
def load_doc_vectors() -> Tuple[Dict[str, Dict[str, float]], Dict[str, float]]:
    # возвращает: (doc_name -> {term: tfidf}), и общий словарь idf
    doc_vecs: Dict[str, Dict[str, float]] = {}
    idf_global: Dict[str, float] = {}

    for fname in os.listdir(TFIDF_DIR):
        if not fname.startswith(FILE_PREFIX):
            continue
        doc_name = fname[len(FILE_PREFIX):-4]  # убираем префикс и .txt
        vec: Dict[str, float] = {}
        with open(os.path.join(TFIDF_DIR, fname), encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                term, idf_str, tfidf_str = line.split()
                idf_val = float(idf_str)
                tfidf_val = float(tfidf_str)
                vec[term] = tfidf_val
                idf_global.setdefault(term, idf_val)
        doc_vecs[doc_name] = vec

    return doc_vecs, idf_global


# загрузка инвертированного индекса: term -> set(docs)
def load_inverted_index(path: str = INVERTED_INDEX_FILE) -> Dict[str, Set[str]]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    # превращаем списки в множества
    return {term: set(docs) for term, docs in data.items()}


# токенизация + лемматизация запроса
def tokenize_query(query: str) -> List[str]:
    words = re.findall(r"[а-яА-ЯёЁ]+", query.lower())
    lemmas: List[str] = []
    for w in words:
        p = _morph.parse(w)[0]
        if p.tag.POS not in IGNORED_POS:
            lemmas.append(p.normal_form)
    return lemmas


# построение TF‑IDF вектора запроса
def query_vector(lemmas: List[str], idf: Dict[str, float]) -> Dict[str, float]:
    cnt = Counter(lemmas)
    total = len(lemmas) or 1
    return {term: (cnt[term] / total) * idf.get(term, 0.0) for term in cnt}


# косинусная близость
def cosine(v1: Dict[str, float], v2: Dict[str, float]) -> float:
    common = set(v1) & set(v2)
    dot = sum(v1[t] * v2[t] for t in common)
    norm1 = math.sqrt(sum(x * x for x in v1.values()))
    norm2 = math.sqrt(sum(x * x for x in v2.values()))
    return dot / (norm1 * norm2) if norm1 and norm2 else 0.0


# выбор кандидатов через инвертированный индекс
def candidate_docs(query_terms: List[str], inv_idx: Dict[str, Set[str]]) -> Set[str]:
    # объединяем списки документов для всех термов запроса
    candidates: Set[str] = set()
    for term in query_terms:
        candidates |= inv_idx.get(term, set())  # объединение множеств с присваиванием
    return candidates


# поиск

def search(query: str, top_k: int = 10):
    # загрузка статических структур
    doc_vecs, idf = load_doc_vectors()
    inv_index = load_inverted_index()

    # подготовка запроса
    q_terms = tokenize_query(query)
    q_vec = query_vector(q_terms, idf)

    # кандидаты по инвертированному индексу
    cand_docs = candidate_docs(q_terms, inv_index)
    if not cand_docs:
        return []  # ни одного совпадения - сразу выход

    # вычисление косинуса только для кандидатов
    scored = [
        (doc, cosine(q_vec, doc_vecs.get(doc, {})))
        for doc in cand_docs
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


# command‑line interface

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python task_5.py \"ваш запрос\" [top_k]")
        sys.exit(0)

    query_text = sys.argv[1]
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    print(f"Запрос: {query_text}\n")
    results = search(query_text, top_k=k)

    if not results:
        print("¯\\_(ツ)_/¯  Документы не найдены")
    else:
        print("Топ результатов:\n-----------------")
        for rank, (doc, score) in enumerate(results, 1):
            print(f"{rank:2}. {doc} — cos={score:.4f}")
