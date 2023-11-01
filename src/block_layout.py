from tkinter.font import Font

from text import Text
from element import Element
from draw_text import DrawText
from draw_rect import DrawRect

HSTEP, VSTEP = 13, 18
WIDTH, HEIGHT = 800, 600
FONTS = {}
BLOCK_ELEMENTS = [
    "html", "body", "article", "section", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
    "footer", "address", "p", "hr", "pre", "blockquote",
    "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
    "figcaption", "main", "div", "table", "form", "fieldset",
    "legend", "details", "summary"
]

class BlockLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []
        self.display_list = []
    
    def layout_mode(self):
        if isinstance(self.node, Text):
            return "inline"
        elif self.node.children:
            if any([isinstance(child, Element) and \
                    child.tag in BLOCK_ELEMENTS
                    for child in self.node.children]):
                return "block"
            else:
                return "inline"
        else:
            return "block"
    
    def layout(self):
        self.x = self.parent.x
        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y
        self.width = self.parent.width
        
        
        mode = self.layout_mode()
        if mode == "block":
            previous = None
            for child in self.node.children:
                next = BlockLayout(child, self, previous)
                self.children.append(next)
                previous = next
        else:
            self.cursor_x = 0
            self.cursor_y = 0
            self.weight = "normal"
            self.style = "roman"
            self.size = 16

            self.line = []
            self.recurse(self.node)
            self.flush()
            
        for child in self.children:
            child.layout()
            
        # calculate height after recursing children
        if mode == "block":
            self.height = sum([child.height for child in self.children])
        else:
            self.height = self.cursor_y
    
    def paint(self, display_list):
        bgcolor = self.node.style.get("background-color",
                                      "transparent")
        if bgcolor != "transparent":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = DrawRect(self.x, self.y, x2, y2, bgcolor)
            display_list.append(rect)
        
        for x, y, word, font, color in self.display_list:
            display_list.append(DrawText(self.x + x, self.y + y,
                                     word, font, color))
        for child in self.children:
            child.paint(display_list)
    
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
            
    def recurse(self, node):
        if isinstance(node, Text):
            for word in node.text.split():
                self.word(node, word)
        else:
            if node.tag == "br":
                self.flush()
            for child in node.children:
                self.recurse(child)
            
    def word(self, node, word: str):
        color = node.style["color"]
        font = self.get_font_wrapper(node)
        w = font.measure(word)
        if self.cursor_x + w > self.width:
            self.flush()
        self.line.append((self.cursor_x, word, font, color))
        self.cursor_x += w + font.measure(" ")
        
    def flush(self):
        """
        Aligns words within buffer along the line, adds all those words to the display list, and
        updates the cursor_x and cursor_y fields.
        """
        if not self.line: return
        metrics = [font.metrics() for x, word, font, color in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent
            
        for x, word, font, color in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font, color))
            
        self.cursor_x = 0
        self.line = []
        
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent
        
    def get_font(self, size, weight, slant) -> Font:
        key = (size, weight, slant)
        if key not in FONTS:
            font = Font(size=size, weight=weight, slant=slant)
            FONTS[key] = font
        return FONTS[key]
    
    def get_font_wrapper(self, node):
        weight = node.style["font-weight"]
        style = node.style["font-style"]
        if style == "normal": style = "roman"
        size = int(float(node.style["font-size"][:-2]) * .75)
        return self.get_font(size, weight, style)
