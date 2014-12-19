import math
import os
import time
import re
import textwrap
from functools import lru_cache
from collections import Counter
from xml.etree import ElementTree
import glob

def get_reuters_stopwords():
    """Retourne une liste de stopwords"""
    root = ElementTree.parse(os.path.join(os.path.dirname(__file__), 'data/stopwords.xml'))
    return set(word.text.lower() for word in root.iter('word'))

class Document:
    """Représente un document"""
    __slots__ = ['title', 'body', 'date', 'terms']

    word_regex = re.compile(r"[\w']+")
    stopwords = get_reuters_stopwords()

    def __init__(self, title, body, date):
        self.title = title
        self.body = body
        self.date = date
        self.terms = Counter([w.lower() for w in self.word_regex.findall(' '.join([self.title, self.body]))])

    @lru_cache()
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
        matching_documents = [document for document in documents if term in document.terms]
        return math.log(len(documents) / len(matching_documents))

    @staticmethod
    def fast_idf(all_doc_nb,matching_doc_nb):
        return math.log(all_doc_nb / matching_doc_nb)

    def tfidf(self, term, documents):
        """
        Calcul le tf-idf d'un terme pour un corpus de documents donné.

        Donne une division par zéro si le terme n'est pas dans le corpus.
        """
        return self.term_frequency(term) * self.inverse_document_frequency(term, documents)

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

def get_reuters_documents():
    """Fetch all Reuteurs document and return a list of Document objects."""

    # on utilise glob pour trouver tous les documents reuters
    files = glob.glob(os.path.join(os.path.dirname(__file__), 'data/reuters21578/reut2-*.xml'))

    begin = time.time()
    docs = []
    for f in sorted(files):
        with open(f, 'rb') as my_file:
            print('Parsing ', f, '...', sep='', end=' ')
            parser = ElementTree.iterparse(my_file)
            for event, article in parser:
                if article.tag in {'REUTERS', 'UNKNOWN'}:
                    date = article.find('DATE')
                    text = article.find('TEXT')

                    # contenu du texte
                    if text is not None:
                        title = text.find('TITLE')
                        author = text.find('AUTHOR')
                        body = text.find('BODY')
                        docs.append(Document(title.text if title is not None else '', body.text if body is not None else '', date.text if date is not None else ''))
        print('{}%'.format(round(len(docs) / 20578 * 100, 2)))

    print('Parsed all articles from Reuters in {}s.'.format(time.time() - begin))
    return docs
