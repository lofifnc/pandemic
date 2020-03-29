from typing import List, Dict, Set


class TrieNode:
    def __init__(self):
        self.end = False
        self.children: Dict[str] = {}

    def all_words(self, prefix):
        if self.end:
            yield prefix

        for letter, child in self.children.items():
            yield from child.all_words(prefix + letter)


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert_set(self, list_of_words: Set[str]):
        for word in list_of_words:
            self.insert(word)

    def insert(self, word: str):
        curr = self.root
        for letter in word:
            node = curr.children.get(letter)
            if not node:
                node = TrieNode()
                curr.children[letter] = node
            curr = node
        curr.end = True

    def clear(self):
        self.root = TrieNode()

    def search(self, word: str):
        curr = self.root
        for letter in word:
            node = curr.children.get(letter, False)
            if not node:
                return False
            curr = node
        return curr.end

    def all_words_beginning_with_prefix(self, prefix: str) -> List[str]:
        cur = self.root
        for c in prefix:
            cur = cur.children.get(c)
            if cur is None:
                return  # No words with given prefix

        yield from cur.all_words(prefix)
