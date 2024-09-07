from bs4 import BeautifulSoup
import re
import string

class PtWiktionaryScraper:
    @staticmethod
    def check_language_is_correct(soup: BeautifulSoup) -> bool:
        main_content = soup.find('div', {'id': 'bodyContent'})

        if main_content.find('h1').get('id') != 'Português':
            correct_language = False
        else:
            correct_language = True

        return correct_language

    @staticmethod
    def get_general_info(soup: BeautifulSoup) -> dict:
        # TODO: implement different wordtypes; only look at noun info for now

        target_header = soup.find('h2', {'id': re.compile('^Substantivo[1]?$')})
        noun_info = target_header.find_next('p').text  # returns dictionary word and gender after , for example :
        noun_info_splitted = noun_info.split(' ')

        if len(noun_info_splitted) != 1:
            lemma = PtWiktionaryScraper._clean_up_text(noun_info_splitted[0])
            gender = PtWiktionaryScraper._clean_up_text(noun_info_splitted[1])
        else:
            lemma = PtWiktionaryScraper._clean_up_text(noun_info_splitted[0])
            gender = 'UNKNOWN'

        pronunciations = []
        # TODO: Handle different regions
        try:
            target_section = soup.find('h2', {'id': 'Pronúncia'})
            target_subsection = target_section.find_next('h3', {'id': 'Portugal'})
            target_list = target_subsection.find_next('ul')

            for p in target_list.find_all('span', {'class': 'ipa'}):
                pronunciations.append(p.text)
        except Exception as e:
            self._log_entry(str(e))
            pronunciations = []

        return {'lemma': lemma, 'gender': gender, 'pronunciations': pronunciations}

    @staticmethod
    def _clean_up_text(text):
        # Create a translation table that maps all punctuation characters to None
        translator = str.maketrans('', '', string.punctuation)
        clean_text = text.translate(translator)

        # Remove punctuation using translate
        translator = str.maketrans('', '', string.digits)
        clean_text = clean_text.translate(translator)

        clean_text = clean_text.strip()

        return clean_text