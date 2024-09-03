import re
import requests
import string
from bs4 import BeautifulSoup


class WiktionaryScraperFR:

    BASE_URL: str = 'https://fr.wiktionary.org/wiki/'
    HEADERS: dict = {'Accept': 'text/html'}
    TYPE: str = 'noun'
    LANGUAGE: str = 'french'

    def __init__(self):
        pass

    def request_word(self, word):


        request_dict: dict = {}
        word_dict: dict = {}

        try:
            soup = self._do_request(word)
            lemma, pronunciation, gender = self._get_general_info(soup)

            word_dict['reference'] = lemma
            word_dict['type'] = self.TYPE
            word_dict['language'] = self.LANGUAGE
            word_dict['gender'] = self._translate_genders(gender)
            word_dict['pronunciations'] = pronunciation

            request_dict['status'] = 'OK'
            # TODO: only noun type is used now
        except Exception as e:
            # self.__log(e)
            request_dict['status'] = 'ERROR'
            request_dict['error'] = str(e)

        finally:
            request_dict['request'] = word
            request_dict['source'] = self.BASE_URL

            response_dict = {'header': request_dict, 'response': word_dict}
            return response_dict

    def _do_request(self, word: str) -> BeautifulSoup:
        request_url: str = self.BASE_URL + word
        response: requests.Response = requests.get(request_url, headers=self.HEADERS)

        if response.status_code != 200:
            raise Exception('Error: requested word returned status code: ' + str(response.status_code))
        else:
            soup = BeautifulSoup(response.content, 'html.parser')

            main_content = soup.find('div', {'id': 'bodyContent'})
            headers = main_content.find_all('span', {'class': 'sectionlangue'})

            if headers[0].get('id') != 'fr' and headers[1].get('id') != 'fr':
                raise Exception('Error: requested word is not in French')

            return soup

    def _get_general_info(self, soup):
        #TODO: implement different wordtypes; only look at noun info for now

        target_header = soup.find('h3', {'id': re.compile('^Nom_commun1?$')})
        noun_info = target_header.find_next('p')

        noun_lemma = noun_info.find('b').text
        noun_pronunciation = noun_info.find_next('span', {'class': 'API'}).text
        noun_gender = noun_info.find_next('i').text

        return noun_lemma,noun_pronunciation,noun_gender
    @staticmethod
    def _translate_genders(gender):
        #TODO: implement gender type enum
        return_gender = -1
        if gender.lower() == 'masculin':
            return_gender =  'masculine'
        elif gender.lower() == 'féminin':
            return_gender =  'feminine'
        else:
            return_gender = 'Error getting gender'

        return return_gender