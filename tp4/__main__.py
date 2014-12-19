import itertools
import numpy as np
import pydoc
import random
import re
import time

from compressed_trie import Trie, make_trie_from_docs 
from document import Document, get_reuters_documents, get_reuters_stopwords

documents = get_reuters_documents()
stopwords = get_reuters_stopwords()
comptrie = make_trie_from_docs(documents)



print('{} documents chargés dans l\'index.'.format(len(documents)))
print('Essayez un des termes suivants:', *random.choice(documents).terms)
print('Pour quitter la boucle interactive, appuyez sur « CTRL-D ».')
print('Une fois dans le pager, tapez sur « q » pour quitter.')

while True:
    try:
        query = input('? ')
    except EOFError:
        print() # print a \n
        break

    terms = re.findall(r"[\w']+", query)

    terms = list(set(terms) - stopwords)

    if not terms:
        print('Aucun termes pertinents on été founi.')
        continue

    print('Termes de la recherche:', ', '.join(terms) + '.')
    
    begin = time.time()

    # on va chercher dans le trie les documents qui contiennent les termes recherchés
    docsearch_vector = {term: comptrie.search(term) for term in terms}
    alldocs_len = len(documents)

    # on assume que le tf de la requête vaut 1
    try:
        query_vector = {term: Document.fast_idf(alldocs_len,len(docs)) for term,docs in docsearch_vector.items()}
    except ZeroDivisionError:
        print('Le(s) terme(s) {} ne sont pas dans le corpus des documents.'.format(', '.join(terms)))
        continue

    # on prend seulement les documents qui ont une intersection entre la requête et leurs termes
    # on doit optimiser cette partie en triant les documents pour accélérer la recherche

    matching_documents = set()
    for doc in docsearch_vector.values():
        matching_documents = matching_documents.union(doc)

    print('{} document(s) trouvé(s) en {}s.'.format(len(matching_documents), time.time() - begin))

    begin = time.time()

    query_vector = np.array([query_vector[term] for term in terms])
    documents_matrix = np.array([[(document.tfidf(term, documents) if term in document.terms else 0) for term in terms] for document in matching_documents])

    print('Vecteur de la requête:', query_vector, sep='\n')
    print('Matrice des documents:', documents_matrix, sep='\n')

    query_vector_norm = np.linalg.norm(query_vector)
    documents_matrix_norm = np.linalg.norm(documents_matrix)


    a = np.dot(documents_matrix, query_vector)
    b= np.multiply(documents_matrix_norm, query_vector_norm)
    # ranking listé par cosinus d'angle
    ranking = np.divide(a, b)
    print('Ranking calculés en {}s.'.format(time.time() - begin))

    # trie du document le plus pertinent au moins pertinent
    matching_documents = sorted(zip(ranking, matching_documents), key=lambda l: l[0], reverse=True)

    while True:
        print('#', 'Ranking', 'Titre', sep='\t')
        for index, (ranking, document) in enumerate(matching_documents):
            print(index, round(ranking, 5), document.title.lower().title(), sep='\t')

        print(len(matching_documents), '-', 'Retour', sep='\t')

        try:
            index = int(input('# '))
        except ValueError:
            print('Votre choix doit être un nombre.')
            continue

        # l'utilisateur choisit « Retour »
        if index == len(matching_documents):
            break

        try:
            ranking, document = matching_documents[index]

            # présente le document avec le pager de pydoc
            pydoc.pager(str(document))

        except IndexError:
            print('Votre choix doit être un nombre entre 0 et {} inclusivement.'.format(len(matching_documents)))
            continue
