from element import Element
from selector import DescendantSelector, TagSelector


INHERITED_PROPERTIES = {
    "font-size": "16px",
    "font-style": "normal",
    "font-weight": "normal",
    "color": "black",
}

def style(node, rules):
    node.style = {}
    
    for property, default_value in INHERITED_PROPERTIES.items():
        if node.parent:
            node.style[property] = node.parent.style[property]
        else:
            node.style[property] = default_value
    
    for selector, body in rules:
        if not selector.matches(node): continue
        for property, value in body.items():
            node.style[property] = value
    
    if isinstance(node, Element) and "style" in node.attributes:
        pairs = CSSParser(node.attributes["style"]).body()
        for property, value in pairs.items():
            node.style[property] = value
            
    if node.style["font-size"].endswith("%"):
        if node.parent:
            parent_font_size = node.parent.style["font-size"]
        else:
            parent_font_size = INHERITED_PROPERTIES["font-size"]
        node_pct = float(node.style["font-size"][:-1]) / 100
        parent_px = float(parent_font_size[:-2])
        node.style["font-size"] = str(node_pct * parent_px) + "px"
            
    for child in node.children:
        style(child, rules)

def cascade_priority(rule):
    selector, body = rule
    return selector.priority

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
        while self.i < len(self.s) and self.s[self.i] != "}":
            try:
                prop, val = self.pair()
                pairs[prop.lower()] = val
                self.whitespace()
                self.literal(";")
                self.whitespace()
            except Exception:
                why = self.ignore_until([";", "}"])
                if why == ";":
                    self.literal(";")
                    self.whitespace()
                else:
                    print(self.s)
                    break
                
        return pairs

    def parse(self):
        rules = []
        while self.i < len(self.s):
            try:
                self.whitespace()
                selector = self.selector()
                self.literal("{")
                self.whitespace()
                body = self.body()
                self.literal("}")
                rules.append((selector, body))
            except Exception:
                why = self.ignore_until(["}"])
                if why == "}":
                    self.literal("}")
                    self.whitespace()
                else:
                    print(self.s)
                    break
        return rules
    
    def selector(self):
        out = TagSelector(self.word().lower())
        self.whitespace()
        while self.i < len(self.s) and self.s[self.i] != "{":
            tag = self.word()
            descendant = TagSelector(tag.lower())
            out = DescendantSelector(out, descendant)
            self.whitespace()
        return out
    
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
        return None

