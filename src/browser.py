import math
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

import ctypes
import sdl2
import skia

from constants import *


with open("browser.css") as f:
    DEFAULT_STYLE_SHEET = CSSParser(f.read()).parse()

class Browser:
    
    def __init__(self) -> None:
        self.chrome = Chrome(self)
        self.display_list: list
        self.scroll = 0
        
        # Old Tkinter implementation
        # self.window = tk.Tk()
        # self.canvas = tk.Canvas(
        #     self.window,
        #     width=WIDTH,
        #     height=HEIGHT,
        #     bg="white"
        # )
        # self.canvas.pack()
        
        # Create an SDL window
        self.sdl_window = sdl2.SDL_CreateWindow(b"Browser", sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, 
                                                WIDTH, HEIGHT, sdl2.SDL_WINDOW_SHOWN)
        
        # Create an SDL surface fir Skia to draw to
        self.root_surface = skia.Surface.MakeRaster(
            skia.ImageInfo.Make(
                WIDTH, HEIGHT,
                ct=skia.kRGBA_8888_ColorType,
                at=skia.kUnpremul_AlphaType
            )
        )
        self.chrome_surface = skia.Surface(WIDTH, math.ceil(self.chrome.bottom))
        self.tab_surface = None
        
        self.url = None
        
        self.tabs = []
        self.active_tab = None
        self.focus = None
        
        if sdl2.SDL_BYTEORDER == sdl2.SDL_BIG_ENDIAN:
            self.RED_MASK = 0xff000000
            self.GREEN_MASK = 0x00ff0000
            self.BLUE_MASK = 0x0000ff00
            self.ALPHA_MASK = 0x000000ff
        else:
            self.RED_MASK = 0x000000ff
            self.GREEN_MASK = 0x0000ff00
            self.BLUE_MASK = 0x00ff0000
            self.ALPHA_MASK = 0xff000000
        
        # Tkinter event binding
        # self.window.bind("<Up>", self.handle_up)
        # self.window.bind("<Down>", self.handle_down)
        # self.window.bind("<MouseWheel>", self.handle_scrollmouse)
        # self.window.bind("<Button-1>", self.handle_click)
        # self.window.bind("<Key>", self.handle_key)
        # self.window.bind("<Return>", self.handle_enter)

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
            self.focus = None
            self.chrome.click(e.x, e.y)
            self.raster_chrome()
            self.raster_tab()
        else:
            if self.focus != "content":
                self.focus = "content"
                self.chrome.blur()
                self.raster_chrome()
            url = self.active_tab.url
            tab_y = e.y - self.chrome.bottom
            self.active_tab.click(e.x, tab_y)
            if self.active_tab.url != url:
                self.raster_chrome()
            self.raster_tab()
        self.draw()
        
    def handle_key(self, char):
        if not (0x20 <= ord(char) < 0x7f): return
        if self.chrome.focus:
            self.chrome.keypress(char)
            self.raster_chrome()
            self.draw()
        elif self.focus == "content":
            self.active_tab.keypress(char)
            self.raster_tab()
            self.draw()
        
    def handle_enter(self):
        if self.chrome.focus:
            self.chrome.enter()
            self.raster_tab()
            self.raster_chrome()
            self.draw()
            
    def handle_backspace(self):
        if self.chrome.focus:
            self.chrome.backspace()
            self.raster_chrome()
            self.draw()
        elif self.focus == "content":
            self.active_tab.backspace()
            self.raster_tab()
            self.draw()
        
    def handle_quit(self):
        sdl2.SDL_DestroyWindow(self.sdl_window)
        
    def raster_tab(self):
        tab_height = math.ceil(self.active_tab.document.height + 2 * VSTEP)

        if not self.tab_surface or tab_height != self.tab_surface.height():
            self.tab_surface = skia.Surface(WIDTH, tab_height)

        canvas = self.tab_surface.getCanvas()
        canvas.clear(skia.ColorWHITE)
        self.active_tab.raster(canvas)

    def raster_chrome(self):
        canvas = self.chrome_surface.getCanvas()
        canvas.clear(skia.ColorWHITE)

        for cmd in self.chrome.paint():
            cmd.execute(canvas)

    def load(self, url: URL) -> None:
        self.new_tab(url)
    
    def draw(self):
        canvas = self.root_surface.getCanvas()
        canvas.clear(skia.ColorWHITE)
        # self.active_tab.draw(canvas, self.chrome.bottom)
        
        tab_rect = skia.Rect.MakeLTRB(0, self.chrome.bottom, WIDTH, HEIGHT)
        tab_offset = self.chrome.bottom - self.active_tab.scroll
        canvas.save()
        canvas.clipRect(tab_rect)
        canvas.translate(0, tab_offset)
        self.tab_surface.draw(canvas, 0, 0)
        canvas.restore()
        
        chrome_rect = skia.Rect.MakeLTRB(0, 0, WIDTH, self.chrome.bottom)
        canvas.save()
        canvas.clipRect(chrome_rect)
        self.chrome_surface.draw(canvas, 0, 0)
        canvas.restore()
        
        # # Draw the chrome display
        # for cmd in self.chrome.paint():
        #     cmd.execute(0, canvas)
            
        # Wrap the data into an SDL surface without copying the bytes
        skia_image = self.root_surface.makeImageSnapshot()
        skia_bytes = skia_image.tobytes()
        
        depth = 32 # Bits per pixel
        pitch = 4 * WIDTH # Bytes per row
        sdl_surface = sdl2.SDL_CreateRGBSurfaceFrom(
            skia_bytes, WIDTH, HEIGHT, depth, pitch,
            self.RED_MASK, self.GREEN_MASK, 
            self.BLUE_MASK, self.ALPHA_MASK
        )
        
        # Draw pixel data to window by blitting (copying) it from sdl_surface to sdl_window's surface
        rect = sdl2.SDL_Rect(0, 0, WIDTH, HEIGHT)
        window_surface = sdl2.SDL_GetWindowSurface(self.sdl_window)
        # SDL_BlitSurface is what actually does the copy
        sdl2.SDL_BlitSurface(sdl_surface, rect, window_surface, rect)
        sdl2.SDL_UpdateWindowSurface(self.sdl_window)
        
    def new_tab(self, url):
        new_tab = Tab(HEIGHT - self.chrome.bottom, self.chrome)
        new_tab.load(url)
        self.tabs.append(new_tab)
        self.active_tab = new_tab
        self.raster_chrome()
        self.raster_tab()
        self.draw()
        
def mainloop(browser: Browser):
    event = sdl2.SDL_Event()
    while True:
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                browser.handle_quit()
                sdl2.SDL_Quit()
                sys.exit()
            elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                browser.handle_click(event.button)
            elif event.type == sdl2.SDL_MOUSEWHEEL:
                if event.wheel.y < 0:
                    browser.handle_down(event)
                elif event.wheel.y > 0:
                    browser.handle_up(event)
            elif event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_RETURN:
                    browser.handle_enter()
                elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                    browser.handle_down(event)
                elif event.key.keysym.sym == sdl2.SDLK_UP:
                    browser.handle_up(event)
                elif event.key.keysym.sym == sdl2.SDLK_BACKSPACE:
                    browser.handle_backspace()
            elif event.type == sdl2.SDL_TEXTINPUT:
                browser.handle_key(event.text.text.decode('utf8'))
        browser.active_tab.task_runner.run()


if __name__ == "__main__":
    import sys
    sdl2.SDL_Init(sdl2.SDL_INIT_EVENTS)
    browser = Browser()
    # Browser().load(URL(sys.argv[1]))
    browser.new_tab(URL(sys.argv[1]))
    browser.draw()
    # tk.mainloop()
    mainloop(browser)