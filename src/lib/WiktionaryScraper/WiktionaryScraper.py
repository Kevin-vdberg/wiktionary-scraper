import string
import requests
from bs4 import BeautifulSoup

from src.lib.WiktionaryScraper.EnWiktionaryScraper import EnWiktionaryScraper
from src.lib.WiktionaryScraper.PtWiktionaryScraper import PtWiktionaryScraper
from src.lib.WiktionaryScraper.FrWiktionaryScraper import FrWiktionaryScraper

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
            return self._check_language_is_function(soup, FrWiktionaryScraper.check_if_language_is_correct)
        elif language == language_types.PT:
            return self._check_language_is_function(soup, PtWiktionaryScraper.check_language_is_correct)
        elif language == language_types.EN:
            return self._check_language_is_function(soup, EnWiktionaryScraper.check_language_is_correct)
        else:
            raise Exception(f'Error: language {language} not supported')

    def _get_word_info(self, soup: BeautifulSoup, language: language_types) -> dict:
        if language == language_types.FR:
            return self._get_general_info_function(soup, FrWiktionaryScraper.get_general_info)
        elif language == language_types.PT:
            return self._get_general_info_function(soup, PtWiktionaryScraper.get_general_info)
        elif language == language_types.EN:
            return self._get_general_info_function(soup, EnWiktionaryScraper.get_general_info)
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

    def _log_entry(self, log_data:str, log_type='DEBUG'):
        if self._logger is None:
            print(f'{log_type}: {log_data}')
        else:
            pass


