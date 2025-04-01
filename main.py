import os
import requests
from tqdm import tqdm

INPUT_FILE = "sites.txt"  # Файл со списком сайтов
OUTPUT_DIR = "downloaded_pages"  # Папка для сохранения
INDEX_FILE = "index.txt"  # Файл формата номер -> ссылка на страницу

# Создаем папку, если её нет
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Читаем список сайтов
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f]

# Открываем индексный файл
with open(INDEX_FILE, "w", encoding="utf-8") as index:
    for i, url in enumerate(tqdm(urls, desc="Downloading pages")):
        try:
            response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()

            file_path = os.path.join(OUTPUT_DIR, f"page_{i}.html")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)

            index.write(f"{i}\t{url}\n")
        except Exception as e:
            print(f"Failed to download {url}: {e}")
