from tkinter.font import Font

from text import Text
from element import Element

HSTEP, VSTEP = 13, 18
WIDTH, HEIGHT = 800, 600
FONTS = {}

class Layout:
    def __init__(self, tree):
        self.display_list = []
        
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 16
        
        self.line = []
        
        self.recurse(tree)
        self.flush()
        
    def open_tag(self, tag):
        if tag == "i":
            self.style = "italic"
        elif tag == "b":
            self.weight = "bold"
        elif tag == "small":
            self.size -= 2
        elif tag == "big":
            self.size += 4
        elif tag == "br":
            self.flush()

    def close_tag(self, tag):
        if tag == "i":
            self.style = "roman"
        elif tag == "b":
            self.weight = "normal"
        elif tag == "small":
            self.size += 2
        elif tag == "big":
            self.size -= 4
        elif tag == "/p":
            self.flush()
            self.cursor_y += VSTEP
            
    def recurse(self, tree):
        if isinstance(tree, Text):
            for word in tree.text.split():
                self.word(word)
        else:
            self.open_tag(tree.tag)
            for child in tree.children:
                self.recurse(child)
            self.close_tag(tree.tag)
            
    def word(self, word: str):
        font = self.get_font(self.size, self.weight, self.style)
        w = font.measure(word)
        if self.cursor_x + w > WIDTH - HSTEP:
            self.flush()
        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")
        
    def flush(self):
        """
        Aligns words within buffer along the line, adds all those words to the display list, and
        updates the cursor_x and cursor_y fields.
        """
        if not self.line: return
        metrics = [font.metrics() for x, word, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent
        
        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))
            
        self.cursor_x = HSTEP
        self.line = []
        
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent
        
    def get_font(self, size, weight, slant) -> Font:
        key = (size, weight, slant)
        if key not in FONTS:
            font = Font(size=size, weight=weight, slant=slant)
            FONTS[key] = font
        return FONTS[key]
