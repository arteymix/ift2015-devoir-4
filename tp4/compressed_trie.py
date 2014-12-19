import time

class Trie:
    """Compressed Prefix Tree"""
    @staticmethod
    def from_documents(documents):
        """Contruit un Trie depuis une liste de documents"""
        begin = time.time()
        c = Trie()
        for doc in documents:
            for term in doc.terms:
                c.add(term, doc)

        print('Trie compressé avec tous les termes pertinents de documents créé en {}s.'.format(time.time() - begin))

        return c

    class Node:
        def __str__(self):
            return "{key: " + self.key + ", val: " + str(self.value) + ", children: (" + '; '.join(str(child) for child in self.children) + ")}"

        def __init__(self, key, element=None):
            self.key=key
            self.children = []
            if element is not None:
                self.value = set()
                self.value.add(element)
            else :
                self.value = None
        #retourne le nombre de match entre le debut de la clé du noeud et la string k en input
        #retourne 0 si aucun match, retourne 1 si la premiere lettre correspond mais différence
        def matchPrefix(self, k):
            i = 0
            for char in self.key:
                if i < len(k) and char == k[i]:
                    i += 1
                else:
                    break
            return i

        def insert(self, key, element):
            added = False
            assert self.matchPrefix(key) == len(self.key)

            if len(key) == len(self.key) :
                if self.value :
                    self.value.add(element)
                else :
                    self.value = set()
                    self.value.add(element)
                return

            truncated_key = key[len(self.key):]
            for child in self.children:
                p = child.matchPrefix(truncated_key)
                #continuer a iterer si le match == 0
                if p == len(child.key) :
                    child.insert(truncated_key,element)
                    added = True
                    break
                elif p > 0:
                    self.children.remove(child)
                    n = Trie.Node(child.key[0:p])
                    child.key = child.key[p:]
                    n.children = [child,Trie.Node(truncated_key[p:], element)]
                    self.children.append(n)
                    added=True
                    break
            if not added:
                self.children.append(Trie.Node(truncated_key, element))

    def __init__(self):
        self.root = self.Node("")

    def add(self, key, element):
        self.root.insert(key,element)

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        """
        Trouve cherche une clé récursivement depuis un noeud donné.
        Retourne False si l'élément n'est pas trouvé
        """
        if node.key == key :
            if node.value is not None:
                return node.value
        else:
            for child in node.children:
                p = child.matchPrefix(key)
                if p == len(key):
                    if child.value is not None :
                        return child.value
                    else : break
                elif p > 0:
                    return self._search(child, key[p:])
        return set()


    def __str__(self):
        return str(self.root)
"""
if __name__ == "__main__":
    t = Trie()
    t.add('asd', 27)
    t.add('asdf', 28)
    t.add('g', 10)
    t.add('asdee', 21)
    t.add('asdeh', 39)
    t.add('asdehh', 20)
    t.add('ga', 20)
    t.add('gagasd', 2)
    print(t)"""
