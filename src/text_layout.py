from utils import get_font, linespace
from draw import DrawText


class LineLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        
        # Children are appended in BlockLayout's word function
        self.children = []
        
    def layout(self):
        self.width = self.parent.width
        self.x = self.parent.x

        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y
            
        for word in self.children:
            word.layout()
            
        if not self.children:
            self.height = 0
            return
            
        max_ascent = max([-word.font.getMetrics().fAscent for word in self.children])
        baseline = self.y + 1.25 * max_ascent
        for word in self.children:
            word.y = baseline - word.font.getMetrics().fAscent
        max_descent = max([word.font.getMetrics().fDescent for word in self.children])
        
        self.height = 1.25 * (max_ascent + max_descent)
        
    def paint(self):
        return []
    
    def paint_effects(self, cmds):
        return cmds


class TextLayout:
    def __init__(self, node, word, parent, previous):
        self.node = node
        self.word = word
        self.children = []
        self.parent = parent
        self.previous = previous
        
    def layout(self):
        weight = self.node.style["font-weight"]
        style = self.node.style["font-style"]
        if style == "normal": style = "roman"
        # size = int(float(self.node.style["font-size"][:-2]) * .75)
        size = float(self.node.style["font-size"][:-2])
        self.font = get_font(size, weight, style)
        
        self.width = self.font.measureText(self.word)

        if self.previous:
            space = self.previous.font.measureText(" ")
            self.x = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x

        self.height = linespace(self.font)
        
    def paint(self):
        cmds = []
        color = self.node.style["color"]
        cmds.append(DrawText(self.x, self.y, self.word, self.font, color))
        return cmds
    
    def paint_effects(self, cmds):
        return cmds
        