from bs4 import BeautifulSoup

class EnWiktionaryScraper:

    @staticmethod
    def check_language_is_correct(soup: BeautifulSoup) -> bool:
        try:
            main_header = soup.find('h2', {'id': 'English'})

            if main_header.get('id') != 'English':
                correct_language = False
            else:
                correct_language = True
            return correct_language;
        except Exception as e:
            return False

    @staticmethod
    def get_general_info(soup: BeautifulSoup) -> dict:

        lemma = EnWiktionaryScraper._get_lemma(soup)
        pronunciations = EnWiktionaryScraper._get_pronunciation(soup)
        gender = 'Unknown'

        return {'lemma': lemma, 'gender': gender, 'pronunciations': pronunciations}
        pass

    @staticmethod
    def _get_pronunciation(soup: BeautifulSoup) -> list:
        pronunciations = []

        main_section = soup.find('h3', {'id': 'Pronunciation'}).find_next('ul')
        list_of_p = main_section.find_all('span',{'class': 'IPA'})

        for p in list_of_p:
            pronunciations.append(p.text)

        return pronunciations

    @staticmethod
    def _get_lemma(soup: BeautifulSoup) -> str:
        main_section = soup.find('h3', {'id': 'Noun'})
        lemma = main_section.find_next('p').find_next('strong',{'class': 'Latn headword'}).text

        return lemma