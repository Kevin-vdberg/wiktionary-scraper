import re
import requests
import string
from bs4 import BeautifulSoup


class WiktionaryScraperPT:

    BASE_URL: str = 'https://pt.wiktionary.org/wiki/'
    HEADERS: dict = {'Accept': 'text/html'}
    TYPE: str = 'noun'
    LANGUAGE: str = 'portuguese'

    def __init__(self):
        pass

    def request_word(self, word):
        request_dict: dict = {}
        word_dict: dict = {}

        try:
            soup = self._do_request(word)
            lemma,gender = self._get_general_info(soup)
            pronunciations = self._get_pronunciations(soup)

            word_dict['reference'] = lemma
            word_dict['type'] = self.TYPE
            word_dict['language'] = self.LANGUAGE
            word_dict['gender'] = self._translate_genders(gender)
            word_dict['pronunciations'] = pronunciations

            request_dict['status'] = 'OK'
            #TODO: only noun type is used now
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

            #check if word is in Portuguese
            if main_content.find('h1').get('id') != 'Português':
                raise Exception('Error: requested word is not in Portuguese')

            return soup

    def _get_pronunciations(self, soup, region='Portugal'):
        pronunciations = []

        #TODO: Handle different regions
        try:
            target_section = soup.find('h2', {'id': 'Pronúncia'})
            target_subsection = target_section.find_next('h3', {'id': region})
            target_list = target_subsection.find_next('ul')

            for p in target_list.find_all('span', {'class': 'ipa'}):
                pronunciations.append(p.text)
        except Exception as e:
            pronunciations = 'Error getting pronunciations'
        finally:
            return pronunciations

    def _get_general_info(self, soup):
        #TODO: implement different wordtypes; only look at noun info for now

        target_header = soup.find('h2', {'id': re.compile('^Substantivo[1]?$')})
        noun_info = target_header.find_next('p').text               #returns dictionary word and gender after , for example :
        noun_info_splitted = noun_info.split(' ')

        if len(noun_info_splitted) != 1:
            lemma = self._clean_up_text(noun_info_splitted[0])
            gender = self._clean_up_text(noun_info_splitted[1])
        else:
            lemma = self._clean_up_text(noun_info_splitted[0])
            gender = 'UNKNOWN'

        return lemma,gender

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

    @staticmethod
    def _translate_genders(gender):
        #TODO: implement gender type enum
        return_gender = -1
        if gender.lower() == 'masculino':
            return_gender =  'masculine'
        elif gender.lower() == 'feminino':
            return_gender =  'feminine'
        else:
            return_gender = 'Error getting gender'

        return return_gender

    @staticmethod
    def __log(log_info, log_type='DEBUG'):
        print(log_info)


