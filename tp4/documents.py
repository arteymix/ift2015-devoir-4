import os
import re
from collections import Counter
from lxml import etree

from stopwords import ReuterStopwords


DEFAULT_STOPWORDS = ReuterStopwords()


def start_tag(name):
    return '<%s>' % name

def end_tag(name):
    return '</%s>' % name

class Document:

    def __init__(self, title, text):
        self._title = title
        self._text = text

    def title(self):
        return self._title

    def text(self):
        return self._text

class DocumentTerms():

    def __init__(self, document, stopwords=DEFAULT_STOPWORDS):
        self._doc = document
        self._terms = Counter([term.lower() for term
                               in re.findall(r"[\w']+", self._doc.text())
                               if term not in stopwords])
                
    def document(self):
        return self._doc

    def __iter__(self):
        return self._terms.items().__iter__()

    def __len__(self):
        return self._terms.__len__()
            
class Documents:    

    def __init__(self, documents):
        self._docs = documents

    def __getitem__(self, k):
        return self._docs[k]

    def __iter__(self):
        return self._docs.__iter__()

    def __len__(self):
        return self._docs.__len__()

class ReuterDocuments(Documents):

    def __init__(self):
        FOLDER = 'reuters21578-2'

        '''The files we'll read: reut2-000.sgm, reut2-001.sgm, ..., reut2-021.sgm.'''
        files = ['reut2-%03d.sgm' % i for i in range(0, 22)]

        FIRST_TAG = 'REUTERS'
        TEXT_TAG = 'TEXT'
        TITLE_TAG = 'TITLE'
        BODY_TAG = 'BODY'
        
        DUMMY_TAG = 'DUMMY'
        dummy_start_tag = start_tag(DUMMY_TAG)
        dummy_end_tag = end_tag(DUMMY_TAG)
        
        parser = etree.XMLParser(recover=True)
        
        docs = []
        for f in files:            
            with open(os.path.join(FOLDER, f), 'rb') as my_file:
                xml = my_file.read().decode(errors='replace')
            xml = xml[xml.find(FIRST_TAG)-1:]
            xml = dummy_start_tag + xml + dummy_end_tag
            
            root = etree.fromstring(xml, parser=parser)
            
            file_docs = []
            texts = list(root.iter(TEXT_TAG))
            for text in texts:
                title = text.find(TITLE_TAG)
                body = text.find(BODY_TAG)
                if title is not None and body is not None:
                    file_docs.append(Document(title.text, body.text))

            print('%d documents read from %s.' % (len(file_docs), f))
            docs.extend(file_docs)

        print('A total of %d documents were read.' % len(docs))
        super().__init__(docs)
