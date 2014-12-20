import itertools
import numpy as np
import pydoc
import random
import re
import time
import string

from document import Document, get_reuters_documents, get_reuters_stopwords
from compressed_trie import Trie

documents = get_reuters_documents()
stopwords = get_reuters_stopwords()
comptrie = Trie(string.ascii_lowercase)

# remplit le trie avec les termes des documents
begin = time.time()
for index, doc in enumerate(documents):
    for term in doc.terms:
        comptrie[term.lower()] = doc
    if index % 100 == 0:
        print('Loaded {} articles in the trie...'.format(index), '{}%'.format(round(index * 100 / len(documents), 2)), sep='\t')

print('Trie compressé avec tous les termes pertinents de documents créé en {}s.'.format(time.time() - begin))

print('{} documents chargés dans l\'index.'.format(len(documents)))
print('Essayez un des termes suivants:', *random.choice(documents).terms)
print('Pour quitter la boucle interactive, appuyez sur « CTRL-D ».')

while True:
    try:
        query = input('? ')
    except EOFError:
        print() # print a \n
        break

    terms = re.findall(r"[\w']+", query.lower())

    terms = list(set(terms) - stopwords)

    if not terms:
        print('Aucun termes pertinents on été founi.')
        continue

    print('Termes de la recherche:', ', '.join(terms) + '.')

    begin = time.time()

    # on va chercher dans le trie les documents qui contiennent les termes recherchés
    docsearch_vector = {term: comptrie.values(term) for term in terms}

    # on assume que le tf de la requête vaut 1
    try:
        query_vector = {term: 0.5 * Document.inverse_document_frequency(term, comptrie) for term, docs in docsearch_vector.items()}
    except ZeroDivisionError:
        print('Le(s) terme(s) {} ne sont pas dans le corpus des documents.'.format(', '.join(terms)))
        continue

    # on prend seulement les documents qui ont une intersection entre la requête et leurs termes
    # on doit optimiser cette partie en triant les documents pour accélérer la recherche
    matching_documents = set()
    for doc in docsearch_vector.values():
        matching_documents = matching_documents.union(doc)

    # on doit préserver l'ordre des documents
    matching_document = list(matching_documents)

    print('{} document(s) trouvé(s) en {}s.'.format(len(matching_documents), time.time() - begin))

    begin = time.time()

    query_vector = np.array([query_vector[term] for term in terms])
    documents_matrix = np.array([[(document.tfidf(term, comptrie) if term in document.terms else 0) for term in terms] for document in matching_documents])

    print('Vecteur de la requête:', query_vector, sep='\n')
    print('Matrice des documents:', documents_matrix, sep='\n')

    query_vector_norm = np.linalg.norm(query_vector)
    documents_matrix_norm = np.linalg.norm(documents_matrix)

    # calcul des produits scalaires et du produit des normes
    a = np.dot(documents_matrix, query_vector)
    b = np.multiply(documents_matrix_norm, query_vector_norm)

    # calcul des ranking par cosinus d'angles (a / b)
    ranking = np.divide(a, b)
    print('Ranking calculés en {}s.'.format(time.time() - begin))

    # trie du document le plus pertinent au moins pertinent en fonction des
    # cosinus d'angles.
    matching_documents = sorted(zip(ranking, matching_documents), key=lambda l: l[0], reverse=True)

    while True:
        print('#', 'Ranking', 'Titre', sep='\t')
        for index, (ranking, document) in enumerate(matching_documents):
            print(index, round(ranking, 5), document.title.lower().title(), sep='\t')

        print('r', '-', 'Retour', sep='\t')
        print('Une fois dans le pager, tapez sur « q » pour quitter.')

        index = input('# ')
        if index == 'r':
            break

        try:
            index = int(index)
        except ValueError:
            print('Votre choix doit être un nombre naturel.')
            continue

        try:
            ranking, document = matching_documents[index]

            # présente le document avec le pager de pydoc
            pydoc.pager(str(document))

        except IndexError:
            print('Votre choix doit être un nombre entre 0 et {} inclusivement.'.format(len(matching_documents) - 1))
            continue
