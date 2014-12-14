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

    # on assume que le tf de la requête vaut 1
    try:
        query_vector = {term: Document.inverse_document_frequency(term, documents) for term in terms}
    except ZeroDivisionError:
        print('Les termes {} ne sont pas dans le corpus des documents.'.format(', '.join(term)))
        continue

    print('Vecteur de la requête:', query_vector)

    # on prend seulement les documents qui ont une intersection entre la requête et leurs termes
    # on doit optimiser cette partie en triant les documents pour accélérer la recherche
    documents_with_term = [document for document in documents if set(terms) & set(document.terms)]

    for document in documents_with_term:
        print('Vecteur du document {}:'.format(document.title), document.pounded_terms(documents))

    while True:
        for index, document in enumerate(documents_with_term):
            print(index, document.title.lower().title())

        print(len(documents_with_term), 'Quitter')

        try:
            index = int(input('# '))
        except ValueError:
            continue

        if index == len(documents_with_term):
            break

        document = documents[index]

        print(document.title.lower().title().center(80))
        print((len(document.title) * '-').center(80))
        print('  ' + document.date.center(80), end='\n\n')

        paragraphs = document.body.split('    ')

        for paragraph in paragraphs:
            print('\n'.join(textwrap.wrap('  ' + paragraph, width=80)), end='\n\n')

