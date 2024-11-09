from typing import Dict, Any

from wiktionaryparser import WiktionaryParser
from deep_translator import GoogleTranslator
from wiktionary_sanakirja_parser import WiktionaryParserFI


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

