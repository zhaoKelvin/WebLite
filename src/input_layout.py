from chrome import DrawLine
from draw_rect import DrawRect
from draw_text import DrawText
from text import Text
from utils import get_font


INPUT_WIDTH_PX = 200

class InputLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.children = []
        self.parent = parent
        self.previous = previous
        
    def layout(self):
        weight = self.node.style["font-weight"]
        style = self.node.style["font-style"]
        if style == "normal": style = "roman"
        size = int(float(self.node.style["font-size"][:-2]) * .75)
        self.font = get_font(size, weight, style)
        
        self.width = INPUT_WIDTH_PX

        if self.previous:
            space = self.previous.font.measure(" ")
            self.x = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x

        self.height = self.font.metrics("linespace")
        
    def paint(self, display_list):
        # Draw the background
        bgcolor = self.node.style.get("background-color", "transparent")

        is_atomic = not isinstance(self.node, Text) and (self.node.tag == "input" or self.node.tag == "button")

        # if not is_atomic:
        #     if bgcolor != "transparent":
        #         x2, y2 = self.x + self.width, self.y + self.height
        #         rect = DrawRect(self.x, self.y, x2, y2, bgcolor)
        #         display_list.append(rect)
        
        x2, y2 = self.x + self.width, self.y + self.height
        rect1 = DrawRect(self.x - 1, self.y - 1, x2 + 1, y2 + 1, 'black')
        if self.node.tag == "input":
            rect2 = DrawRect(self.x, self.y, x2, y2, 'orange')
        else:
            rect2 = DrawRect(self.x, self.y, x2, y2, 'cyan')
        display_list.append(rect1)
        display_list.append(rect2)
            
        # Get the input element's text contents
        if self.node.tag == "input":
            text = self.node.attributes.get("value", "")
        elif self.node.tag == "button":
            if len(self.node.children) == 1 and isinstance(self.node.children[0], Text):
                text = self.node.children[0].text
            else:
                print("Ignoring HTML contents inside button")
                text = ""
                
        # Draw the text
        color = self.node.style["color"]
        display_list.append(
            DrawText(self.x, self.y, text, self.font, color))
        
        # If input element is focused, draw cursor
        if self.node.is_focused:
            cx = self.x + self.font.measure(text)
            display_list.append(DrawLine(
                cx, self.y, cx, self.y + self.height, "black", 1))
