from element import Element

def selector(self):
    out = TagSelector(self.word().lower())
    self.whitespace()
    while self.i < len(self.s) and self.s[self.i] != "{":
        tag = self.word()
        descendant = TagSelector(tag.lower())
        out = DescendantSelector(out, descendant)
        self.whitespace()
    return out

class TagSelector:
    def __init__(self, tag):
        self.tag = tag
        self.priority = 1
        
    def matches(self, node) -> bool:
        """
        Returns true if node matches TagSelector object's tag. Else returns false.
        """
        return isinstance(node, Element) and self.tag == node.tag

class DescendantSelector:
    def __init__(self, ancestor, descendant):
        self.ancestor = ancestor
        self.descendant = descendant
        self.priority = ancestor.priority + descendant.priority
        
    def matches(self, node):
        """
        Recursively travels through tag ancestors until matching to a tag.
        """
        if not self.descendant.matches(node): return False
        while node.parent:
            if self.ancestor.matches(node.parent): return True
            node = node.parent
        return False