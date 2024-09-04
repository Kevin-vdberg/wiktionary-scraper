import string
import re
import requests
from bs4 import BeautifulSoup
from src.lib.WiktionaryScraper.types.Genders import Genders as gender_types
from src.lib.WiktionaryScraper.types.Languages import Languages as language_types
from src.lib.WiktionaryScraper.types.WordTypes import WordTypes as word_types
from typing import Callable

class WiktionaryScraper:
    GENDER_CONVERSIONS: dict = {
            gender_types.MASCULINE: ['masculin', 'masculino'],
            gender_types.FEMININE: ['féminin', 'feminino']
        }
    BASE_URL: string.Template = string.Template('https://$lang.wiktionary.org/wiki/')
    REQUEST_HEADERS:dict = {'Accept': 'text/html'}

    _logger = None

    def __init__(self, logger=None):
        pass

    def __str__(self):
        pass

#Public functions
    def request_word(self, word: str, language: language_types) -> dict:
        #Initialze return dictionaries
        request_info = {}
        response_data = {}

        try:
            #Set request specific parameters
            request_url: str = self.BASE_URL.substitute(lang=language.name.lower())
            request_info['lang'] = language.name
            request_info['source'] = request_url
            request_info['request'] = word

            response_data['type'] = word_types.NOUN.value
            response_data['language'] = language.value

            #Do request
            soup = self._do_request(word, request_url)
            correct_language = self._check_language(soup, language)

            if correct_language:
                general_info: dict = self._get_word_info(soup, language)

                response_data['lemma'] = general_info['lemma']
                response_data['gender'] = general_info['gender']
                response_data['pronunciations'] = general_info['pronunciations']
                request_info['status'] = 'OK'

        except Exception as e:
            request_info['status'] = 'ERROR'
            request_info['error_msg'] = e
        finally:
            return_data = {'request_info': request_info, 'response_data': response_data}

            return return_data

    def _do_request(self, word: str, base_url: str):
        request_url: str = base_url + word
        response: requests.Response = requests.get(request_url, headers=self.REQUEST_HEADERS)

        if response.status_code != 200:
            raise Exception('Error: requested word returned status code: ' + str(response.status_code))
        else:
            soup = BeautifulSoup(response.content, 'html.parser')

            return soup

    def _check_language(self,soup: BeautifulSoup, language: language_types) -> bool:

        if language == language_types.FR:
            return self._check_language_is_function(soup, self._check_language_is_french)
        elif language == language_types.PT:
            return self._check_language_is_function(soup, self._check_language_is_portuguese)
        else:
            raise Exception(f'Error: language {language} not supported')

    def _get_word_info(self, soup: BeautifulSoup, language: language_types) -> dict:
        if language == language_types.FR:
            return self._get_general_info_function(soup, self._get_general_info_french)
        elif language == language_types.PT:
            return self._get_general_info_function(soup, self._get_general_info_portuguese)
        else:
            raise Exception(f'Error: language {language} not supported')


#Language specific functions
    # TODO: implement a better log function to handle potential errors
    # TODO: potentially this function can determine the language instead of raising error when not finding one
    def _check_language_is_function(self, soup: BeautifulSoup, check_language: Callable[[BeautifulSoup], bool]) -> bool:
        correct_language: bool = False
        try:
            correct_language = check_language(soup)
            return correct_language
        except Exception as e:
            self._log_entry(str(e))
            raise Exception('Error: cannot verify that requested word is in the requested language: ' + str(e))


    def _get_general_info_function(self,soup: BeautifulSoup, get_info: Callable[[BeautifulSoup], dict]) -> dict:

        try:
            general_info: dict = get_info(soup)
            general_info['gender']=self._translate_found_genders(general_info['gender'])

            return general_info
        except Exception as e:
            self._log_entry(str(e))
            raise Exception('Error while scraping word: ' + str(e))


    #Language checks, because all wiktionary websites are different, the actual scraping varies per language
    # TODO: These functions could be transferred to a language specific static class?

    #French
    def _check_language_is_french(self,soup: BeautifulSoup) -> bool:
            main_content = soup.find('div', {'id': 'bodyContent'})
            headers = main_content.find_all('span', {'class': 'sectionlangue'})

            if headers[0].get('id') != 'fr' and headers[1].get('id') != 'fr':
                correct_language = False
            else:
                correct_language = True

            return correct_language
    def _get_general_info_french(self, soup) -> dict:
        #TODO: implement different wordtypes; only look at noun info for now

        target_header = soup.find('h3', {'id': re.compile('^Nom_commun1?$')})
        noun_info = target_header.find_next('p')

        lemma = noun_info.find('b').text
        pronunciations = [noun_info.find_next('span', {'class': 'API'}).text]
        gender = noun_info.find_next('i').text

        return {'lemma': lemma, 'gender': gender, 'pronunciations': pronunciations}
    #Portuguese
    def _check_language_is_portuguese(self, soup: BeautifulSoup) -> bool:
        main_content = soup.find('div', {'id': 'bodyContent'})

        if main_content.find('h1').get('id') != 'Português':
            correct_language = False
        else:
            correct_language = True

        return correct_language
    def _get_general_info_portuguese(self, soup: BeautifulSoup) -> dict:
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
#General class functions
    def _translate_found_genders(self,gender: str) -> gender_types:

        if gender.lower() in self.GENDER_CONVERSIONS[gender_types.MASCULINE]:
            return_gender =  gender_types.MASCULINE.value
        elif gender.lower() in self.GENDER_CONVERSIONS[gender_types.FEMININE]:
            return_gender =  gender_types.FEMININE.value
        # elif gender.lower() == 'unknown':
        #     return_gender = 'Cannot find gender'
        else:
            self._log_entry(f'Error translating gender: {gender}')
            return_gender =  ''

        return return_gender
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

    def _log_entry(self, log_data:str, log_type='DEBUG'):
        if self._logger is None:
            print(f'{log_type}: {log_data}')
        else:
            pass


