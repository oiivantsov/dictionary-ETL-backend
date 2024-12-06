import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator


def extract_synonyms_from_li(li_element):
    synonyms_list = ""
    synonyms = li_element.find(class_="synonym")
    if synonyms:
        spans = synonyms.find_all('span')
        for span in spans[1:]:
            synonyms_list += span.text + ", "
    return synonyms_list


def extract_examples_from_li(li_element):
    examples = ""
    examples_fi = li_element.find_all(class_="e-example")
    examples_eng = li_element.find_all(class_="e-translation")
    if examples_fi:
        for i in range(len(examples_fi)):
            examples += examples_fi[i].get_text() + " --- " + examples_eng[i].get_text() + " || "

    return examples


class WiktionaryParserENG:
    def __init__(self):
        self.url = "https://en.wiktionary.org/wiki/{}"
        self.session = requests.Session()

    def fetch(self, search_word):
        response = self.session.get(self.url.format(search_word))

        if response.status_code != 200:
            return {"definitions": ''}

        soup = BeautifulSoup(response.text.replace('>\n<', '><'), 'html.parser')

        # a starting point for further definition search
        word_tag = soup.find("strong", class_="Latn headword", lang="fi")

        # return if word is not found
        if word_tag is None:
            return {"definitions": ''}

        # strings to collect data
        definitions_en = ""
        examples = ""
        synonyms = ""
        part_of_speech = word_tag.find_previous('h3').text
        etymology = word_tag.find_previous(id='Etymology')
        etymology = etymology.parent.next_sibling.text if etymology and etymology.parent and etymology.parent.next_sibling else ""

        # definitions and examples

        definitions_list = word_tag.find_next('ol').find_all('li')

        for index, definition in enumerate(definitions_list):
            examples += extract_examples_from_li(definition)
            synonyms += extract_synonyms_from_li(definition)
            # delete dl-element with examples and synonyms
            dl = definition.find("dl")
            if dl:
                dl.decompose()
            # add definitions to def string
            if len(definitions_list) == 1:
                definitions_en += definition.get_text()
                break
            if index == len(definitions_list) - 1:
                definitions_en += f"{index + 1}) {definition.get_text()}"
            else:
                definitions_en += f"{index + 1}) {definition.get_text()}, "

        definitions_ru = GoogleTranslator(source='en', target='ru').translate(definitions_en)
        definitions = definitions_ru + "\n" + definitions_en

        # final formatting
        if examples != '':
            examples = "(wikiENG) |  " + examples
            examples = examples[:-4]

        if synonyms != '':
            synonyms = synonyms[:-2]

        return {
            "definitions": definitions,
            "PoS": part_of_speech,
            "examples": examples,
            "synonyms": synonyms,
            "etymology": etymology
        }

wp = WiktionaryParserENG()
res_dict = wp.fetch('saali')
for (k, v) in res_dict.items():
    print(k, v)