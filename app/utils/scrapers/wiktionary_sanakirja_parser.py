import requests
from bs4 import BeautifulSoup


class WiktionaryParserFI:
    def __init__(self):
        self.url = "https://fi.wiktionary.org/wiki/{}"
        self.session = requests.Session()

    def fetch(self, search_word):
        response = self.session.get(self.url.format(search_word))
        soup = BeautifulSoup(response.text.replace('>\n<', '><'), 'html.parser')

        ordered_list_with_definitions = soup.find('ol')

        if ordered_list_with_definitions:
            li_elements_with_examples = ordered_list_with_definitions.find_all('li')

            word_data = []
            i = 1

            for li in li_elements_with_examples:
                examples = []

                try:
                    dd_all = li.find_all('dd')
                    for dd in dd_all:
                        example = dd.get_text()
                        examples.append(example)

                except AttributeError:
                    pass

                try:
                    dl_el = li.find('dl')
                    dl_el.extract()
                except AttributeError:
                    pass

                definition = li.get_text().rstrip()

                word_data.append({
                    "id": i,
                    "definition": definition,
                    "examples": examples
                })

                i += 1

            definition_message = ""
            examples_message = ""

            for i in word_data:
                definition_message += f"{i['id']}) {i['definition']}, "
                if i['examples']:
                    examples_message += f"{i['id']}) "
                    for j in i['examples']:
                        examples_message += f"{j} / "

                    examples_message = examples_message[:-2]

            definition_message = definition_message[:-2]

            if len(li_elements_with_examples) == 1:
                definition_message = definition_message[3:]
                examples_message = examples_message[3:]

            if definition_message:
                definition_message = "(wikiFI) | " + definition_message

            if examples_message:
                examples_message = "(wikiFI) | " + examples_message

            return {
                "definitions": definition_message,
                "examples": examples_message,
            }

        else:
            return {
                "definitions": "",
                "examples": "",
            }