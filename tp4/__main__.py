import re
import textwrap

from document import Document, get_reuters_documents, get_reuters_stopwords

documents = get_reuters_documents()
stopwords = get_reuters_stopwords()

print(', '.join(stopwords))

for document in documents:
    for term, count in sorted(document.terms.items()):
        print('{}:\t{}'.format(count, term))

for document in documents:
    for term, count in sorted(document.pounded_terms(documents).items()):
        print('{}:\t{}'.format(count, term))

print('<CTRL-D> pour quitter.')

while True:
    query = input('? ')

    terms = re.findall(r"[\w']+", query)

    print('Termes de la recherche:', ', '.join(terms))

    # ici, il faut construire un vecteur de recherche au lieu de montrer tous les documents
    for term in terms:
        try:
            print('idf:', Document.inverse_document_frequency(term, documents))
        except ZeroDivisionError:
            print('Le terme {} n\'est pas dans le corpus des documents'.format(term))
            continue

        documents_with_term = [document for document in documents if term in document.terms]

        for index, document in enumerate(documents_with_term):
            print(index, document.title.lower().title())

        index = int(input('# '))
        document = documents[index]

        print(document.title.lower().title().center(80))
        print((len(document.title) * '-').center(80))
        print('  ' + document.date.center(80), end='\n\n')

        paragraphs = document.body.split('    ')

        for paragraph in paragraphs:
            print('\n'.join(textwrap.wrap('  ' + paragraph, width=80)), end='\n\n')

