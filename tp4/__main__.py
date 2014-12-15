import itertools
import numpy as np
import pydoc
import random
import re
import time

from document import Document, get_reuters_documents, get_reuters_stopwords

documents = get_reuters_documents()
stopwords = get_reuters_stopwords()

print('{} documents chargés dans l\'index.'.format(len(documents)))
print('Essayez', *random.choice(documents).terms)
print('Une fois dans le pager, tapez sur « q » pour quitter.')
print('Pour quitter la boucle interactive, appuyez sur « CTRL-D ».')

while True:
    try:
        query = input('? ')
    except EOFError:
        print() # print a \n
        break

    terms = re.findall(r"[\w']+", query)

    if not terms:
        print('Aucun terme fourni.')
        continue

    print('Termes de la recherche:', ', '.join(terms) + '.')

    # on assume que le tf de la requête vaut 1
    try:
        query_vector = {term: Document.inverse_document_frequency(term, documents) for term in terms}
    except ZeroDivisionError:
        print('Le(s) terme(s) {} ne sont pas dans le corpus des documents.'.format(', '.join(terms)))
        continue

    # on prend seulement les documents qui ont une intersection entre la requête et leurs termes
    # on doit optimiser cette partie en triant les documents pour accélérer la recherche
    begin = time.time()
    documents_with_term = [document for document in documents if set(terms) & set(document.terms)]

    print('{} document(s) trouvé(s) en {}s.'.format(len(documents_with_term), time.time() - begin))

    begin = time.time()

    query_vector = np.array([query_vector[term] for term in terms])
    documents_matrix = np.array([[(document.tfidf(term, documents) if term in document.terms else 0) for term in terms] for document in documents_with_term])

    print('Vecteur de la requête:', query_vector, sep='\n')
    print('Matrice des documents:', documents_matrix, sep='\n')

    query_vector_norm = np.linalg.norm(query_vector)
    documents_matrix_norm = np.linalg.norm(documents_matrix)

    # ranking listé par cosinus d'angle
    ranking = np.divide(np.dot(documents_matrix, query_vector), np.multiply(documents_matrix_norm, query_vector_norm))
    print('Ranking calculés en {}s.'.format(time.time() - begin))

    # trie du document le plus pertinent au moins pertinent
    ordered_documents = sorted(zip(ranking, documents_with_term), key=lambda l: l[0], reverse=True)

    while True:
        print('#', 'Ranking', 'Titre', sep='\t')
        for index, (ranking, document) in enumerate(ordered_documents):
            print(index, round(ranking, 5), document.title.lower().title(), sep='\t')

        print(len(documents_with_term), '-', 'Retour', sep='\t')

        try:
            index = int(input('# '))
        except ValueError:
            print('Votre choix doit être un nombre.')
            continue

        # l'utilisateur choisit « Retour »
        if index == len(documents_with_term):
            break

        try:
            document = documents_with_term[index]
        except IndexError:
            print('Votre choix doit être un nombre entre 0 et {} inclusivement.'.format(len(documents_with_term)))
            continue

        # présente le document avec le pager de pydoc
        pydoc.pager(str(document))
