import urllib3
from cssparser import CSSParser, cascade_priority, style
from document_layout import DocumentLayout
from element import Element
from htmlparser import HTMLParser
from text import Text
from url import URL
from utils import tree_to_list

HSTEP, VSTEP = 13, 18
WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100

with open("browser.css") as f:
    DEFAULT_STYLE_SHEET = CSSParser(f.read()).parse()

class Tab:
    def __init__(self, tab_height):
        self.tab_height = tab_height
        self.history = []
        self.focus = None
    
    def scrollup(self) -> None:
        self.scroll = max(self.scroll - SCROLL_STEP, 0)

    def scrolldown(self):
        max_y = max(self.document.height + 2 * VSTEP - self.tab_height, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)
        
    def scrollmouse(self, delta) -> None:
        if delta > 0:
            self.scroll = max(self.scroll - SCROLL_STEP, 0)
        else:
            max_y = max(self.document.height + 2 * VSTEP - self.tab_height, 0)
            self.scroll = min(self.scroll + SCROLL_STEP, max_y)
        
    def click(self, x, y):
        y += self.scroll
        objs = [obj for obj in tree_to_list(self.document, [])
                if obj.x <= x < obj.x + obj.width
                and obj.y <= y < obj.y + obj.height]
        if not objs: return
        elt = objs[-1].node
        while elt:
            if isinstance(elt, Text):
                pass
            elif elt.tag == "a" and "href" in elt.attributes:
                url = self.url.resolve(elt.attributes["href"])
                return self.load(url)
            elif elt.tag == "input":
                if self.focus:
                    self.focus.is_focused = False
                self.focus = elt
                elt.is_focused = True
                elt.attributes["value"] = ""
                return self.render()
            elif elt.tag == "button":
                # walk up HTML tree to find the form the button is in
                while elt:
                    if elt.tag == "form" and "action" in elt.attributes:
                        return self.submit_form(elt)
                    elt = elt.parent
            elt = elt.parent
            
    def keypress(self, char):
        if self.focus:
            self.focus.attributes["value"] += char
            self.render()
            
    def submit_form(self, elt):
        inputs = [node for node in tree_to_list(elt, [])
                  if isinstance(node, Element)
                  and node.tag == "input"
                  and "name" in node.attributes]
        body = ""
        for input in inputs:
            name = input.attributes["name"]
            value = input.attributes.get("value", "")
            # name = urllib3.parse.quote(name)
            # value = urllib3.parse.quote(value)
            body += "&" + name + "=" + value
        body = body[1:]
        url = self.url.resolve(elt.attributes["action"])
        self.load(url, body)
        
    def go_back(self):
        if len(self.history) > 1:
            self.history.pop()
            back = self.history.pop()
            self.load(back)    
            
    def load(self, url: URL, payload=None) -> None:
        self.url = url
        self.scroll = 0
        self.history.append(url)
        
        # Parse HTML
        headers, body = url.request(payload)
        self.nodes = HTMLParser(body).parse()
        
        # Parse CSS
        self.rules = DEFAULT_STYLE_SHEET.copy()
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
            self.rules.extend(CSSParser(body).parse())
            
        self.render()
        
    def render(self):
        style(self.nodes, sorted(self.rules, key=cascade_priority))
        
        # Load HTML Tree into Layout Tree
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        self.document.paint(self.display_list)
            
    def draw(self, canvas, offset):
        for cmd in self.display_list:
            if cmd.top > self.scroll + self.tab_height:
                continue
            if cmd.bottom < self.scroll: continue
            cmd.execute(self.scroll - offset, canvas)