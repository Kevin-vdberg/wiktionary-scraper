from bs4 import BeautifulSoup

class EsWiktionaryScraper:

    @staticmethod
    def check_language_is_correct(soup: BeautifulSoup) -> bool:
        main_content = soup.find('div', {'id': 'bodyContent'})

        if main_content.find('h1').get('id') != 'Español':
            correct_language = False
        else:
            correct_language = True

        return correct_language