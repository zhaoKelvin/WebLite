from element import Element


def style(node):
    node.style = {}
    
    if isinstance(node, Element) and "style" in node.attributes:
        pairs = CSSParser(node.attributes["style"]).body()
        for property, value in pairs.items():
            node.style[property] = value
            
    for child in node.children:
        style(child)

class CSSParser:
    """
    Parses CSS in HTML tags. Stores information parsed and parser's current location.
    """
    def __init__(self, s):
        self.s = s
        self.i = 0
        
    def whitespace(self):
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1
            
    def word(self):
        start = self.i
        while self.i < len(self.s):
            if self.s[self.i].isalnum() or self.s[self.i] in "#-.%":
                self.i += 1
            else:
                break
        if not (self.i > start):
            raise Exception("Parsing error")
        return self.s[start:self.i]

    def literal(self, literal):
        if not (self.i < len(self.s) and self.s[self.i] == literal):
            raise Exception("Parsing error")
        self.i += 1
        
    def pair(self):
        """
        Parses a single property-value pair. Returns the property and value.
        """
        prop = self.word()
        self.whitespace()
        self.literal(":")
        self.whitespace()
        val = self.word()
        return prop.lower(), val

    def body(self):
        pairs = {}
        while self.i < len(self.s):
            try:
                prop, val = self.pair()
                pairs[prop.lower()] = val
                self.whitespace()
                self.literal(";")
                self.whitespace()
            except Exception:
                why = self.ignore_until([";"])
                if why == ";":
                    self.literal(";")
                    self.whitespace()
                else:
                    break
                
        return pairs

    def ignore_until(self, chars):
        """
        Stops at any one of a set of characters, 
        and returns that character (or None if it was stopped by the end of the file)
        """
        while self.i < len(self.s):
            if self.s[self.i] in chars:
                return self.s[self.i]
            else:
                self.i += 1

