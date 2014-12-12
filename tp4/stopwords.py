import xml.etree.ElementTree as ET


class Stopwords:

    def __init__(self, words):
        self._words = set([word.lower() for word in words])

    def __len__(self):
        return len(self._words)

    def __contains__(self, word):
        return word.lower() in self._words

    def add(self, word):
        self._words.add(word)

class DefaultStopwords(Stopwords):

    def __init__(self):
        tree = ET.parse('stopwords')
        root = tree.getroot()
        stopwords = [word.text for word in root.iter('word')]
        super().__init__(stopwords)

class ReuterStopwords(DefaultStopwords):

    def __init__(self):
        super().__init__()
        self.add('reuter')
