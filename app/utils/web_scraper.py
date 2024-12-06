from typing import Dict, Any

from app.utils.scrapers.wiktionary_sanakirja_parser import WiktionaryParserFI
from app.utils.scrapers.wiktionary_eng_parser import WiktionaryParserENG
from app.utils.scrapers.urban_scraper import UrbanScraper

def fetch_wiki_FI(search_word: str):
    parser_fi = WiktionaryParserFI()
    return parser_fi.fetch(search_word)

def fetch_wiki_ENG(search_word: str) -> Dict[str, Any]:
    parser_fi = WiktionaryParserENG()
    return parser_fi.fetch(search_word)

def fetch_slang(search_word: str) -> Dict[str, Any]:
    scraper_urban = UrbanScraper()
    return scraper_urban.fetch(search_word)