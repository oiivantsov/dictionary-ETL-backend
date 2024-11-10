from typing import Dict, Any

from wiktionaryparser import WiktionaryParser
from deep_translator import GoogleTranslator
from wiktionary_sanakirja_parser import WiktionaryParserFI
from bs4 import BeautifulSoup
import re, requests


def fetch_wiki_FI(search_word: str):
    parser_fi = WiktionaryParserFI()
    return parser_fi.fetch(search_word)


# Функция для парсинга данных с английской Wiki
def fetch_wiki_ENG(search_word: str) -> Dict[str, Any]:
    parser = WiktionaryParser()
    parser.set_default_language('Finnish')
    wiki_data = parser.fetch(search_word, 'Finnish')
    if not wiki_data or not wiki_data[0]:
        return {"error": "No data found"}

    etymology = wiki_data[0].get("etymology", "")
    definitions = wiki_data[0].get("definitions", [])

    if not definitions:
        return {"error": "No definitions found"}

    part_of_speech = definitions[0].get("partOfSpeech", "")
    all_definitions = definitions[0].get("text", [])[1:]

    examples_and_synonyms = definitions[0].get("examples", [])
    examples = [ex for ex in examples_and_synonyms if not ex.startswith("Synonyms")]
    synonyms = [syn.replace("Synonyms: ", "").replace("Synonym: ", "") for syn in examples_and_synonyms if
                syn.startswith("Synonyms") or syn.startswith("Synonym")]

    definitions_to_eng = ", ".join(all_definitions)
    definitions_to_rus = GoogleTranslator(source='en', target='ru').translate(definitions_to_eng)
    definitions_excel = f"{definitions_to_rus} \n{definitions_to_eng}"

    examples_excel = " // ".join(examples)
    synonyms_excel = ", ".join(synonyms)

    return {
        "definitions": definitions_excel,
        "PoS": part_of_speech,
        "examples": examples_excel,
        "synonyms": synonyms_excel,
        "etymology": etymology
    }

def fetch_slang(search_word: str) -> Dict[str, Any]:
    # Обработка слова для вставки в URL
    formatted_word = format_word_for_url(search_word)

    # URL для парсинга страницы
    url = f"https://urbaanisanakirja.com/word/{formatted_word}"
    response = requests.get(url)

    # Проверка успешности запроса
    if response.status_code != 200:
        return {"error": "Unable to fetch data"}

    # Парсинг контента страницы
    soup = BeautifulSoup(response.text, "html.parser")

    # Название слова
    try:
        word_name = soup.select_one(".box h1").text
    except AttributeError:
        word_name = "n/a"

    # Сбор всех описаний и соответствующих лайков и дизлайков
    descriptions = [desc.text.strip() for desc in soup.select(".box p")]
    likes_list = [extract_count(like) for like in soup.select(".rate-up")]
    dislikes_list = [extract_count(dislike) for dislike in soup.select(".rate-down")]

    # Формируем описание с лайками и дизлайками для каждого элемента
    if len(descriptions) > 1:
        description_texts = [
            f"{i+1}) {desc} ({likes_list[i]}/{dislikes_list[i]})"
            for i, desc in enumerate(descriptions)
            if i < len(likes_list) and i < len(dislikes_list)
        ]
        description_text = "(urbaani) | " + " | ".join(description_texts)
    elif descriptions:
        description_text = f"(urbaani) | {descriptions[0]} ({likes_list[0]}/{dislikes_list[0]})"
    else:
        description_text = ""  # Пустая строка, если описаний нет

    # Сбор всех примеров
    examples = [ex.text.strip().replace("\n", "").replace("  ", " ") for ex in soup.select(".box blockquote")]
    if len(examples) > 1:
        example_text = "(urbaani) | " + " | ".join([f"{i+1}) {ex}" for i, ex in enumerate(examples)])
    elif examples:
        example_text = f"(urbaani) | {examples[0]}"
    else:
        example_text = ""  # Пустая строка, если примеров нет

    # Формат возвращаемых данных
    return {
        "word": word_name,
        "description": description_text,
        "example": example_text,
    }

def format_word_for_url(word: str) -> str:
    # Замена специальных символов
    word = word.lower()
    word = word.replace("ä", "a").replace("ö", "o").replace("å", "a")
    word = re.sub(r"\s+", "-", word)  # Заменяем пробелы на дефисы
    return word

def extract_count(element) -> int:
    try:
        count_str = element.text
        if 'K' in count_str:
            count = float(count_str.replace('K', '').replace(',', '.')) * 1000
        else:
            count = int(count_str.replace(',', ''))
    except (AttributeError, ValueError):
        count = 0
    return count
