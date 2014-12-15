import math
import os
import textwrap
import time
import re
from collections import Counter
from lxml.etree import XMLParser, parse
import glob

# utilise un parser « safe »
parser = XMLParser(recover=True)

class Document:
    """Représente un document"""
    def __init__(self, title, body, date):
        self.title = title
        self.body = body
        self.date = date

        terms = re.findall(r"[\w']+", ' '.join([self.title, self.body]))
        stopwords = get_reuters_stopwords()
        self.terms = Counter([term for term in terms if term.lower() not in stopwords])

    def term_frequency(self, term):
        """Retourne la fréquence d'un terme donné dans le document"""
        total = sum(self.terms.values())

        return 0.5 + (0.5 * self.terms[term] / total) / (max(self.terms.values()) / total)

    @staticmethod
    def inverse_document_frequency(term, documents):
        """
        Calcule la fréquence d'un terme dans les autres documents.

        Le logarithme sert à mettre les données à l'échelle de term_frequency
        dans la fonction tfidf.

        Si le terme n'est pas dans aucun des documents, il va y avoir une
        division par zéro.
        """
        documents_with_term = [document for document in documents if term in document.terms]
        return math.log(len(documents) / len(documents_with_term))

    def tfidf(self, term, documents):
        """
        Calcul le tf-idf d'un terme pour un corpus de documents donné.

        Donne une division par zéro si le terme n'est pas dans le corpus.
        """
        return self.term_frequency(term) * self.inverse_document_frequency(term, documents)

    def pounded_terms(self, documents):
        """
        Retourne un dictionnaire où la clé et un terme et la valeur le poids du
        terme dans le document
        """
        return {term: self.tfidf(term, documents) for term in self.terms}

    def __cmp__(self, other):
        """
        Compare ce document avec un autre document afin de pouvoir trier une
        liste de documents.
        """
        raise NotImplementedError

    def __str__(self):
        # rendu du document
        formatted_document = self.title.lower().title().center(80) + '\n'
        formatted_document += (len(self.title) * '-').center(80) + '\n'
        formatted_document += self.date.center(80) + '\n\n'

        paragraphs = self.body.split('    ')

        for paragraph in paragraphs:
            formatted_document += '\n'.join(textwrap.wrap('  ' + paragraph, width=80))
            formatted_document += '\n\n'

        return formatted_document

def get_reuters_stopwords():
    """Retourne une liste de stopwords"""
    root = parse(os.path.join(os.path.dirname(__file__), 'data/stopwords.xml'), parser)
    return [word.text for word in root.iter('word')]


def get_reuters_documents():
    """Fetch all Reuteurs document and return a list of Document objects."""

    # on utilise glob pour trouver tous les documents reuters
    files = glob.glob(os.path.join(os.path.dirname(__file__), 'data/reuters21578/reut2-*.sgm'))

    begin = time.time()
    docs = []
    for f in files:
        with open(f, 'r') as my_file:
            root = parse(my_file, parser)
            for reuters in root.iter('REUTERS'):
                date = reuters.find('DATE')
                text = reuters.find('TEXT')

                # contenu du texte
                if text is not None:
                    dateline = text.find('DATELINE')
                    title = text.find('TITLE')
                    body = text.find('BODY')
                    if title is not None and body is not None:
                        docs.append(Document(title.text, body.text, date.text))
                    else:
                        print('Le document {} n\'est pas correctement formé'.format(reuters.text))
            else:
                print('{} ne contient pas de documents.'.format(f))

    print('Parsed {} documents from Reuters in {}s'.format(len(docs), time.time() - begin))
    return docs
