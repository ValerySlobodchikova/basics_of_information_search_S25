import json
import re
import pymorphy2


class BooleanSearch:
    def __init__(self, index_path):
        self.morph = pymorphy2.MorphAnalyzer()
        with open(index_path, encoding='utf-8') as f:
            self.index = json.load(f)
        self.all_docs = set()
        for postings in self.index.values():
            self.all_docs.update(postings)

    def term(self, word):
        return set(self.index.get(word.lower(), []))

    def parse_query(self, query):
        query = query.replace("and", " & ").replace("or", " | ")

        tokens = re.findall(r'\w+|\(|\)|\&|\|', query)
        parsed = []
        skip_next = False

        for i, token in enumerate(tokens):
            if skip_next:
                skip_next = False
                continue

            if token.upper() == 'NOT':
                if i + 1 < len(tokens):
                    term = tokens[i + 1]
                    parsed.append(f"(self.all_docs - self.term(\"{term}\"))")
                    skip_next = True
            elif token in {'&', '|', '(', ')'}:
                parsed.append(token)
            else:
                parsed.append(
                    f"self.term(\"{self.morph.parse(token)[0].normal_form}\")")  # поиск с приведением токена в нф
                # parsed.append(f"self.term(\"{token}\")") # поиск без приведения токена в нф

        return ' '.join(parsed)

    def execute(self, query):
        parsed = self.parse_query(query)
        return sorted(eval(parsed))


if __name__ == '__main__':
    search = BooleanSearch('../../Downloads/inverted_index.json')
    print("Введите булевый запрос. Примеры:")
    print("(Клеопатра AND Цезарь) OR (Антоний AND Цицерон)")
    print("NOT Помпей AND Цезарь\n")

    while True:
        q = input("Запрос (или 'exit'): ")
        if q.lower() == 'exit':
            break
        results = search.execute(q.lower())
        print(f"Найдено в документах ({len(results)}): {results}\n")
