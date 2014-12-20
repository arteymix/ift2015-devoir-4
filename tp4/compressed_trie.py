import string
import os

class Trie:
    """
    Implémentation de trie par arbre.
    """
    class Node:
        """
        Noeud contenant un caractère de la trie.
        """
        def __init__(self, key='', element=None):
            self.key = key
            self.children = []
            self.value = {element} if element is not None else element

        def common_prefix(self, k):
            """
            Retourne la longueur du préfix commun entre la clé interne et une
            clé k fournie.
            """
            return os.path.commonprefix([self.key, k])

        def insert(self, key, element):
            assert len(self.common_prefix(key)) == len(self.key)

            if len(key) == len(self.key):
                if self.value:
                    self.value.add(element)
                else:
                    self.value = set()
                    self.value.add(element)
                return

            truncated_key = key[len(self.key):]
            for child in self.children:
                p = len(child.common_prefix(truncated_key))
                #continuer a iterer si le match == 0
                if p == len(child.key):
                    child.insert(truncated_key, element)
                    return
                elif p > 0:
                    self.children.remove(child)
                    n = Trie.Node(child.key[0:p])
                    child.key = child.key[p:]
                    n.children = [child, Trie.Node(truncated_key[p:], element)]
                    self.children.append(n)
                    return

            self.children.append(Trie.Node(truncated_key, element))

    def __init__(self, alphabet=string.ascii_lowercase):
        self.root = Trie.Node()
        self.size = 0

    def values(self, key):
        """Return values matching a given key"""
        return self._search(self.root, key)

    def _search(self, node, key):
        """
        Trouve cherche une clé récursivement depuis un noeud donné.
        Retourne False si l'élément n'est pas trouvé
        """
        if node.key == key:
            if node.value is not None:
                return node.value
        else:
            for child in node.children:
                p = len(child.common_prefix(key))
                if p == len(key):
                    if child.value is not None:
                        return child.value
                    else: break
                elif p > 0:
                    return self._search(child, key[p:])
        return set()

    def __in__(self, key):
        return len(self.values(key)) > 0

    def __getitem__(self, key):
        return self.values(key)[0]

    def __setitem__(self, key, value):
        self.root.insert(key, value)
        self.size += 1

    def __len__(self):
        return self.size

    def __str__(self):
        return str(self.root)
