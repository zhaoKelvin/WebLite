from block_layout import BlockLayout


HSTEP, VSTEP = 13, 18
WIDTH, HEIGHT = 800, 600

class DocumentLayout:
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.children = []

    def layout(self):
        child = BlockLayout(self.node, self, None)
        self.children.append(child)
        
        self.width = WIDTH - 2 * HSTEP
        self.x = HSTEP
        self.y = VSTEP
        child.layout()
        self.height = child.height + 2 * VSTEP
        
    def paint(self, display_list):
        self.children[0].paint(display_list)