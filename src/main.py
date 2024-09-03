import string

from src.lib.WiktionaryScraper.FrenchScraper.WiktionaryScraperFR import WiktionaryScraperFR
from src.lib.WiktionaryScraper.PortugueseScraper.WiktionaryScraperPT import WiktionaryScraperPT

def main():
    # words = get_list_of_common_words()[20:50]
    #
    # for word in words:
    #     result = WiktionaryScraperPT().request_word(word)
    #     print(result)
    portuguese_words = ['árvore','rosa','peixe','fogo','pardal']
    french_words = ['arbre', 'rose', 'poisson','feu','moineau']

    pt_scraper = WiktionaryScraperPT()
    fr_scraper = WiktionaryScraperFR()

    for x in range(5):
        pt = pt_scraper.request_word(portuguese_words[x])
        fr = fr_scraper.request_word(french_words[x])

        print(pt)
        print(fr)


def get_list_of_common_words():
    file = open('../static/words.txt', 'r')
    words = file.readlines()
    file.close()

    words = [word.strip('\n') for word in words]
    return words

if __name__ == '__main__':
    main()
