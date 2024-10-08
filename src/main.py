import string
from src.lib.WiktionaryScraper.WiktionaryScraper import WiktionaryScraper
from src.lib.WiktionaryScraper.types.Languages import Languages


def main():
    words = get_list_of_common_words()[0:50]
    # words = ['tree','rose','fish','fire']

    # translator = Translator()
    words = ['parapluie', 'baguette','eau']
    # translator.translate('appel')
    scraper = WiktionaryScraper()
    #
    for word in words:
        print (scraper.request_word(word,Languages.FR))


def get_list_of_common_words():
    file = open('../static/words.txt', 'r')
    words = file.readlines()
    file.close()

    words = [word.strip('\n') for word in words]
    return words


if __name__ == '__main__':
    main()
