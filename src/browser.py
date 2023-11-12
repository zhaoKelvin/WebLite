from chrome import Chrome
from element import Element
from tab import Tab
from text import Text
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

with open("browser.css") as f:
    DEFAULT_STYLE_SHEET = CSSParser(f.read()).parse()

class Browser:
    
    def __init__(self) -> None:
        
        self.display_list: list
        self.scroll = 0
        
        self.window = tk.Tk()
        self.canvas = tk.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT,
            bg="white"
        )
        self.canvas.pack()
        
        self.url = None
        
        self.tabs = []
        self.active_tab = None
        
        self.chrome = Chrome(self)
        
        self.window.bind("<Up>", self.handle_up)
        self.window.bind("<Down>", self.handle_down)
        self.window.bind("<MouseWheel>", self.handle_scrollmouse)
        self.window.bind("<Button-1>", self.handle_click)
        self.window.bind("<Key>", self.handle_key)
        self.window.bind("<Return>", self.handle_enter)

    def handle_up(self, e):
        self.active_tab.scrollup()
        self.draw()

    def handle_down(self, e):
        self.active_tab.scrolldown()
        self.draw()
        
    def handle_scrollmouse(self, e):
        self.active_tab.scrollmouse(e.delta)
        self.draw()
        
    def handle_click(self, e):
        if e.y < self.chrome.bottom:
            self.chrome.click(e.x, e.y)
        else:
            tab_y = e.y - self.chrome.bottom
            self.active_tab.click(e.x, tab_y)
        self.draw()
        
    def handle_key(self, e):
        if len(e.char) == 0: return
        if not (0x20 <= ord(e.char) < 0x7f): return
        self.chrome.keypress(e.char)
        self.draw()
        
    def handle_enter(self, e):
        self.chrome.enter()
        self.draw()

    def load(self, url: URL) -> None:
        self.new_tab(url)
    
    def draw(self):
        self.canvas.delete("all")
        self.active_tab.draw(self.canvas, self.chrome.bottom)
        
        # Draw the chrome display
        for cmd in self.chrome.paint():
            cmd.execute(0, self.canvas)
        
    def new_tab(self, url):
        new_tab = Tab(HEIGHT - self.chrome.bottom)
        new_tab.load(url)
        self.active_tab = new_tab
        self.tabs.append(new_tab)
        self.draw()
        


if __name__ == "__main__":
    import sys
    Browser().load(URL(sys.argv[1]))
    tk.mainloop()