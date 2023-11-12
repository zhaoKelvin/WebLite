from draw_rect import DrawRect
from draw_text import DrawText
from url import URL
from utils import get_font

WIDTH, HEIGHT = 800, 600

class Chrome:
    def __init__(self, browser):
        self.browser = browser
        
        self.focus = None
        self.address_bar = ""
        
        self.font = get_font(20, "normal", "roman")
        self.font_height = self.font.metrics("linespace")
        
        self.padding = 5
        self.tabbar_top = 0
        self.tabbar_bottom = self.font_height + 2 * self.padding
        self.bottom = self.tabbar_bottom
        
        plus_width = self.font.measure("+") + 2 * self.padding
        self.newtab_rect = (
           self.padding, self.padding,
           self.padding + plus_width,
           self.padding + self.font_height
        )
        
        self.urlbar_top = self.tabbar_bottom
        self.urlbar_bottom = self.urlbar_top + \
            self.font_height + 2*self.padding
        self.bottom = self.urlbar_bottom
        
        back_width = self.font.measure("<") + 2*self.padding
        self.back_rect = (
            self.padding,
            self.urlbar_top + self.padding,
            self.padding + back_width,
            self.urlbar_bottom - self.padding,
        )

        self.address_rect = (
            self.back_rect[2] + self.padding,
            self.urlbar_top + self.padding,
            WIDTH - self.padding,
            self.urlbar_bottom - self.padding,
        )
        
    def tab_rect(self, i):
        tabs_start = self.newtab_rect[3] + self.padding
        tab_width = self.font.measure("Tab X") + 2 * self.padding
        return (
            tabs_start + tab_width * i, self.tabbar_top,
            tabs_start + tab_width * (i + 1), self.tabbar_bottom
        )
        
    def paint(self):
        cmds = []
        
        # tabs bar
        cmds.append(DrawRect(
            0, 0, WIDTH, self.bottom,
            "white"))
        cmds.append(DrawLine(
            0, self.bottom, WIDTH,
            self.bottom, "black", 1))
        
        # "+"" button
        cmds.append(DrawOutline(
            self.newtab_rect[0], self.newtab_rect[1],
            self.newtab_rect[2], self.newtab_rect[3],
            "black", 1))
        cmds.append(DrawText(
            self.newtab_rect[0] + self.padding,
            self.newtab_rect[1],
            "+", self.font, "black"))
        
        # tabs
        for i, tab in enumerate(self.browser.tabs):
            bounds = self.tab_rect(i)
            cmds.append(DrawLine(
                bounds[0], 0, bounds[0], bounds[3],
                "black", 1))
            cmds.append(DrawLine(
                bounds[2], 0, bounds[2], bounds[3],
                "black", 1))
            cmds.append(DrawText(
                bounds[0] + self.padding, bounds[1] + self.padding,
                "Tab {}".format(i), self.font, "black"))
            if tab == self.browser.active_tab:
                cmds.append(DrawLine(
                    0, bounds[3], bounds[0], bounds[3],
                    "black", 1))
                cmds.append(DrawLine(
                    bounds[2], bounds[3], WIDTH, bounds[3],
                    "black", 1))
                
        # back button
        cmds.append(DrawOutline(
            self.back_rect[0], self.back_rect[1],
            self.back_rect[2], self.back_rect[3],
            "black", 1))
        cmds.append(DrawText(
            self.back_rect[0] + self.padding,
            self.back_rect[1],
            "<", self.font, "black"))
        
        # address bar
        cmds.append(DrawOutline(
            self.address_rect[0], self.address_rect[1],
            self.address_rect[2], self.address_rect[3],
            "black", 1))
        if self.focus == "address bar":
            cmds.append(DrawText(
                self.address_rect[0] + self.padding,
                self.address_rect[1],
                self.address_bar, self.font, "black"))
            
            # cursor
            w = self.font.measure(self.address_bar)
            cmds.append(DrawLine(
                self.address_rect[0] + self.padding + w,
                self.address_rect[1],
                self.address_rect[0] + self.padding + w,
                self.address_rect[3],
                "red", 1))

        else:
            url = str(self.browser.active_tab.url)
            cmds.append(DrawText(
                self.address_rect[0] + self.padding,
                self.address_rect[1],
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
    
def intersects(x, y, rect):
    (left, top, right, bottom) = rect
    return x >= left and x < right and y >= top and y < bottom


class DrawOutline:
    def __init__(self, x1, y1, x2, y2, color, thickness):
        self.top = y1
        self.left = x1
        self.bottom = y2
        self.right = x2
        self.color = color
        self.thickness = thickness

    def execute(self, scroll, canvas):
        canvas.create_rectangle(
            self.left, self.top - scroll,
            self.right, self.bottom - scroll,
            width=self.thickness,
            outline=self.color,
        )
        
        
class DrawLine:
    def __init__(self, x1, y1, x2, y2, color, thickness):
        self.top = y1
        self.left = x1
        self.bottom = y2
        self.right = x2
        self.color = color
        self.thickness = thickness

    def execute(self, scroll, canvas):
        canvas.create_line(
            self.left, self.top - scroll,
            self.right, self.bottom - scroll,
            fill=self.color, width=self.thickness,
        )
