from bs4 import BeautifulSoup
import re, requests


def format_word_for_url(word: str) -> str:
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


class UrbanScraper:
    def __init__(self):
        self.url = "https://urbaanisanakirja.com/word/{}"
        self.session = requests.Session()

    def fetch(self, search_word):
        formatted_word = format_word_for_url(search_word)
        response = self.session.get(self.url.format(formatted_word))

        if response.status_code != 200:
            return {"error": "Unable to fetch data"}

        soup = BeautifulSoup(response.text, "html.parser")

        try:
            word_name = soup.select_one(".box h1").text
        except AttributeError:
            word_name = "n/a"

        descriptions = [desc.text.strip() for desc in soup.select(".box p")]
        likes_list = [extract_count(like) for like in soup.select(".rate-up")]
        dislikes_list = [extract_count(dislike) for dislike in soup.select(".rate-down")]

        if len(descriptions) > 1:
            description_texts = [
                f"{i + 1}) {desc} ({likes_list[i]}/{dislikes_list[i]})"
                for i, desc in enumerate(descriptions)
                if i < len(likes_list) and i < len(dislikes_list)
            ]
            description_text = "(urbaani) | " + " | ".join(description_texts)
        elif descriptions:
            description_text = f"(urbaani) | {descriptions[0]} ({likes_list[0]}/{dislikes_list[0]})"
        else:
            description_text = ""

        examples = [ex.text.strip().replace("\n", "").replace("  ", " ") for ex in soup.select(".box blockquote")]
        if len(examples) > 1:
            example_text = "(urbaani) | " + " | ".join([f"{i + 1}) {ex}" for i, ex in enumerate(examples)])
        elif examples:
            example_text = f"(urbaani) | {examples[0]}"
        else:
            example_text = ""

        return {
            "word": word_name,
            "description": description_text,
            "example": example_text,
        }
