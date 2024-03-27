from draw import *
from url import URL
from text_layout import get_font
import skia
from utils import linespace

WIDTH, HEIGHT = 800, 600

class Chrome:
    def __init__(self, browser):
        self.browser = browser
        
        self.focus = None
        self.address_bar = ""
        
        self.font = get_font(20, "normal", "roman")
        self.font_height = linespace(self.font)
        
        self.padding = 5
        self.tabbar_top = 0
        self.tabbar_bottom = self.font_height + 2 * self.padding
        self.bottom = self.tabbar_bottom
        
        plus_width = self.font.measureText("+") + 2 * self.padding
        self.newtab_rect = skia.Rect.MakeLTRB(
           self.padding, self.padding,
           self.padding + plus_width,
           self.padding + self.font_height
        )
        
        self.urlbar_top = self.tabbar_bottom
        self.urlbar_bottom = self.urlbar_top + \
            self.font_height + 2*self.padding
        self.bottom = self.urlbar_bottom
        
        back_width = self.font.measureText("<") + 2*self.padding
        self.back_rect = skia.Rect.MakeLTRB(
            self.padding,
            self.urlbar_top + self.padding,
            self.padding + back_width,
            self.urlbar_bottom - self.padding,
        )

        self.address_rect = skia.Rect.MakeLTRB(
            self.back_rect.top() + self.padding,
            self.urlbar_top + self.padding,
            WIDTH - self.padding,
            self.urlbar_bottom - self.padding,
        )
        
    def tab_rect(self, i):
        tabs_start = self.newtab_rect.right() + self.padding
        tab_width = self.font.measureText("Tab X") + 2 * self.padding
        return skia.Rect.MakeLTRB(
            tabs_start + tab_width * i, self.tabbar_top,
            tabs_start + tab_width * (i + 1), self.tabbar_bottom
        )
        
    def paint(self):
        cmds = []
        
        # tabs bar
        cmds.append(DrawRect(skia.Rect.MakeLTRB(0, 0, WIDTH, self.bottom), "white"))
        cmds.append(DrawLine(
            0, self.bottom, WIDTH,
            self.bottom, "black", 1))
        
        # "+"" button
        cmds.append(DrawOutline(self.newtab_rect, "black", 1))
        cmds.append(DrawText(
            self.newtab_rect.left() + self.padding,
            self.newtab_rect.top(),
            "+", self.font, "black"))
        
        # tabs
        for i, tab in enumerate(self.browser.tabs):
            bounds = self.tab_rect(i)
            cmds.append(DrawLine(
                bounds.left(), 0, bounds.left(), bounds.bottom(),
                "black", 1))
            cmds.append(DrawLine(
                bounds.right(), 0, bounds.right(), bounds.bottom(),
                "black", 1))
            cmds.append(DrawText(
                bounds.left() + self.padding, bounds.top() + self.padding,
                "Tab {}".format(i), self.font, "black"))
            if tab == self.browser.active_tab:
                cmds.append(DrawLine(
                    0, bounds.bottom(), bounds.left(), bounds.bottom(),
                    "black", 1))
                cmds.append(DrawLine(
                    bounds.right(), bounds.bottom(), WIDTH, bounds.bottom(),
                    "black", 1))
                
        # back button
        cmds.append(DrawOutline(self.back_rect, "black", 1))
        cmds.append(DrawText(
            self.back_rect.left() + self.padding,
            self.back_rect.top(),
            "<", self.font, "black"))
        
        # address bar
        cmds.append(DrawOutline(self.address_rect, "black", 1))
        if self.focus == "address bar":
            cmds.append(DrawText(
                self.address_rect.left() + self.padding,
                self.address_rect.top(),
                self.address_bar, self.font, "black"))
            
            # cursor
            w = self.font.measureText(self.address_bar)
            cmds.append(DrawLine(
                self.address_rect.left() + self.padding + w,
                self.address_rect.top(),
                self.address_rect.left() + self.padding + w,
                self.address_rect.bottom(),
                "red", 1))

        else:
            url = str(self.browser.active_tab.url)
            cmds.append(DrawText(
                self.address_rect.left() + self.padding,
                self.address_rect.top(),
                url, self.font, "black"))
                
        return cmds
    
    def click(self, x, y):
        self.focus = None
        if intersects(x, y, self.newtab_rect):
            self.browser.new_tab(URL("https://browser.engineering/"))
        elif intersects(x, y, self.back_rect):
            self.browser.active_tab.go_back()
        elif intersects(x, y, self.address_rect):
            self.focus = "address bar"
            self.address_bar = ""
        else:
            for i, tab in enumerate(self.browser.tabs):
                if intersects(x, y, self.tab_rect(i)):
                    self.browser.active_tab = tab
                    break
                
    def keypress(self, char):
        if self.focus == "address bar":
            self.address_bar += char
            
    def enter(self):
        if self.focus == "address bar":
            self.browser.active_tab.load(URL(self.address_bar))
            self.focus = None
            
    def backspace(self):
        if self.focus == "address bar":
            if len(self.address_bar) > 0:
                self.address_bar = self.address_bar[:-1]
            
    def blur(self):
        self.focus = None
    
def intersects(x, y, rect):
    (left, top, right, bottom) = rect
    return x >= left and x < right and y >= top and y < bottom

