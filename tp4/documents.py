import math
import os
import time
import re
from collections import Counter
from lxml.etree import XMLParser, parse
import glob
from pkgutil import get_data

# utilise un parser « safe »
parser = XMLParser(recover=True)

class Document:
    """Représente un document"""
    def __init__(self, title, body):
        self.title = title
        self.body = body

    def terms(self):
        """
        Retourne les termes du document sous forme d'un Counter en excluant les
        stopwords.
        """
        terms = re.findall(r"[\w']+", ' '.join([self.title, self.body]))
        stopwords = get_reuters_stopwords()
        return Counter([term for term in terms if term not in stopwords])

    def term_frequency(self, term):
        """Retourne la fréquence d'un terme donné dans le document"""
        terms = self.terms()
        total = sum(terms.values())

        return 0.5 + (0.5 * terms[term] / total) / (max(terms.values()) / total)

    def inverse_document_frequency(self, term, documents):
        documents_with_term = [document for document in documents if term in document.terms()]
        return math.log(len(documents) / (1 + len(documents_with_term)))
        pass

    def tfidf(self, term, documents):
        return self.term_frequency(term) * self.inverse_document_frequency(term, documents)

    def pounded_terms(self, documents):
        """
        Retourne un dictionnaire où la clé et un terme et la valeur le poids du
        terme dans le document
        """
        return {term: self.tfidf(term, documents) for term in self.terms()}

    def __cmp__(self, other):
        """
        Compare ce document avec un autre document afin de pouvoir trier une 
        liste de documents.
        """
        pass

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
            for text in root.iter('TEXT'):
                title = text.find('TITLE')
                body = text.find('BODY')
                if title is not None and body is not None:
                    docs.append(Document(title.text, body.text))
            else:
                print('{} ne contient pas de texte.'.format(f))

    print('Parsed {} documents from Reuters in {}s'.format(len(docs), time.time() - begin))
    return docs
