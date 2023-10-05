from url import URL
import tkinter as tk
from typing import List
from layout import Layout

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

    def scrollup(self, e) -> None:
        self.scroll -= SCROLL_STEP
        self.draw()

    def scrolldown(self, e) -> None:
        self.scroll += SCROLL_STEP
        self.draw()

    def load(self, url: URL) -> None:
        headers, body = url.request()
        tokens = url.lex(body)
        self.display_list = Layout(tokens).display_list
        self.draw()
    
    def draw(self):
        self.canvas.delete("all")
        for x, y, w, f in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=w, font=f, anchor='nw')



if __name__ == "__main__":
    import sys
    Browser().load(URL(sys.argv[1]))
    tk.mainloop()