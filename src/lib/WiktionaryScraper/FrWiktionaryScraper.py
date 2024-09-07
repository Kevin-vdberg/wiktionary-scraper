from bs4 import BeautifulSoup
import re

class FrWiktionaryScraper:

    @staticmethod
    def check_if_language_is_correct(soup:BeautifulSoup) -> bool:
        main_content = soup.find('div', {'id': 'bodyContent'})
        headers = main_content.find_all('span', {'class': 'sectionlangue'})

        if headers[0].get('id') != 'fr' and headers[1].get('id') != 'fr':
            correct_language = False
        else:
            correct_language = True

        return correct_language

    @staticmethod
    def get_general_info(soup) -> dict:
        #TODO: implement different wordtypes; only look at noun info for now

        target_header = soup.find('h3', {'id': re.compile('^Nom_commun1?$')})
        noun_info = target_header.find_next('p')

        lemma = noun_info.find('b').text
        pronunciations = [noun_info.find_next('span', {'class': 'API'}).text]
        gender = noun_info.find_next('i').text

        return {'lemma': lemma, 'gender': gender, 'pronunciations': pronunciations}

