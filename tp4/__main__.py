from documents import get_reuters_documents, get_reuters_stopwords

documents = get_reuters_documents()
stopwords = get_reuters_stopwords()

for document in documents:
    print(document.terms())
