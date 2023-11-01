from element import Element
from url import URL
import tkinter as tk
from typing import List
from htmlparser import HTMLParser
from document_layout import DocumentLayout
from cssparser import CSSParser, cascade_priority, style
from utils import tree_to_list

HSTEP, VSTEP = 13, 18
WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100

class Browser:
    
    def __init__(self) -> None:
        
        self.display_list: list
        self.scroll = 0
        
        self.window = tk.Tk()
        self.canvas = tk.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()
        
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<Down>", self.scrolldown)
        
        self.window.bind("<MouseWheel>", self.scrollmouse)
        
        with open("browser.css") as f:
            self.default_style_sheet = CSSParser(f.read()).parse()

        
    def scrollmouse(self, e) -> None:
        if e.delta > 0:
            self.scroll = max(self.scroll - SCROLL_STEP / 2, 0)
            self.draw()
        else:
            max_y = max(self.document.height - HEIGHT, 0)
            self.scroll = min(self.scroll + SCROLL_STEP / 2, max_y)
            self.draw()

    def scrollup(self, e) -> None:
        self.scroll = max(self.scroll - SCROLL_STEP, 0)
        self.draw()

    def scrolldown(self, e) -> None:
        max_y = max(self.document.height - HEIGHT, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)
        self.draw()

    def load(self, url: URL) -> None:
        # Parse HTML
        headers, body = url.request()
        self.nodes = HTMLParser(body).parse()
        
        # Parse CSS
        rules = self.default_style_sheet.copy()
        links = [node.attributes["href"]
                for node in tree_to_list(self.nodes, [])
                if isinstance(node, Element)
                and node.tag == "link"
                and "href" in node.attributes
                and node.attributes.get("rel") == "stylesheet"]

        for link in links:
            try:
                header, body = url.resolve(link).request()
            except:
                continue
            rules.extend(CSSParser(body).parse())
        style(self.nodes, sorted(rules, key=cascade_priority))

        
        # Load DOM Tree
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        self.document.paint(self.display_list)
        self.draw()
    
    def draw(self):
        self.canvas.delete("all")
        for cmd in self.display_list:
            if cmd.top > self.scroll + HEIGHT: continue
            if cmd.bottom < self.scroll: continue
            cmd.execute(self.scroll, self.canvas)



if __name__ == "__main__":
    import sys
    Browser().load(URL(sys.argv[1]))
    tk.mainloop()