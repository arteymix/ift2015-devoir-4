from document import get_reuters_documents, get_reuters_stopwords

documents = get_reuters_documents()
stopwords = get_reuters_stopwords()

print(', '.join(stopwords))

for document in documents:
    for term, count in sorted(document.terms.items()):
        print('{}:\t{}'.format(count, term))

for document in documents:
    for term, count in sorted(document.pounded_terms(documents).items()):
        print('{}:\t{}'.format(count, term))
