import urllib.parse
from cssparser import CSSParser, cascade_priority, style
from document_layout import DocumentLayout
from element import Element
from htmlparser import HTMLParser
from jscontext import JSContext
from text import Text
from url import URL
from utils import paint_tree, tree_to_list
import dukpy

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
        print("clicked in the tab")
        self.focus = None
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
                if self.js.dispatch_event("click", elt): return
                url = self.url.resolve(elt.attributes["href"])
                print("pressed link")
                return self.load(url)
            elif elt.tag == "input":
                if self.js.dispatch_event("click", elt): return
                if self.focus:
                    self.focus.is_focused = False
                self.focus = elt
                elt.is_focused = True
                elt.attributes["value"] = ""
                return self.render()
            elif elt.tag == "button":
                if self.js.dispatch_event("click", elt): return
                # walk up HTML tree to find the form the button is in
                while elt:
                    if elt.tag == "form" and "action" in elt.attributes:
                        return self.submit_form(elt)
                    elt = elt.parent
            elt = elt.parent
            
    def keypress(self, char):
        if self.focus:
            if self.js.dispatch_event("keydown", self.focus): return
            self.focus.attributes["value"] += char
            self.render()
            
    def submit_form(self, elt):
        if self.js.dispatch_event("submit", elt): return
        
        inputs = [node for node in tree_to_list(elt, [])
                  if isinstance(node, Element)
                  and node.tag == "input"
                  and "name" in node.attributes]
        body = ""
        for input in inputs:
            name = input.attributes["name"]
            value = input.attributes.get("value", "")
            name = urllib.parse.quote(name)
            value = urllib.parse.quote(value)
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
        headers, body = url.request(self.url, payload)
        self.nodes = HTMLParser(body).parse()
        
        # Extract and Parse Content-Security-Policy header
        self.allowed_origins = None
        if "content-security-policy" in headers:
            csp = headers["content-security-policy"].split()
            if len(csp) > 0 and csp[0] == "default-src":
                self.allowed_origins = []
                for origin in csp[1:]:
                    self.allowed_origins.append(URL(origin).origin())
        
        # Parse CSS
        self.rules = DEFAULT_STYLE_SHEET.copy()
        links = [node.attributes["href"]
                for node in tree_to_list(self.nodes, [])
                if isinstance(node, Element)
                and node.tag == "link"
                and "href" in node.attributes
                and node.attributes.get("rel") == "stylesheet"]

        for link in links:
            style_url = url.resolve(link)
            if not self.allowed_request(style_url):
                print(style_url)
                print(f"Blocked script {link} due to CSP")
                continue
            try:
                header, body = style_url.request(url)
            except:
                continue
            self.rules.extend(CSSParser(body).parse())
            
        # Parse Javascript
        scripts = [node.attributes["src"] 
                   for node in tree_to_list(self.nodes, [])
                   if isinstance(node, Element)
                   and node.tag == "script"
                   and "src" in node.attributes]
        
        self.js = JSContext(self)
        for script in scripts:
            script_url = url.resolve(script)
            if not self.allowed_request(script_url):
                print(f"Blocked script {script} due to CSP")
                continue
            header, body = script_url.request(url)
            try:
                self.js.run(body)
            except dukpy.JSRuntimeError as e:
                print(f"Script {script} crashed {e}")
        
        self.render()
        
    def render(self):
        style(self.nodes, sorted(self.rules, key=cascade_priority))
        
        # Load HTML Tree into Layout Tree
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
            
    # def draw(self, canvas, offset):
    #     for cmd in self.display_list:
    #         if cmd.rect.top() > self.scroll + self.tab_height:
    #             continue
    #         if cmd.rect.bottom() < self.scroll: continue
    #         cmd.execute(self.scroll - offset, canvas)
            
    def raster(self, canvas):
        for cmd in self.display_list:
            cmd.execute(canvas)
            
    def allowed_request(self, url: URL):
        return self.allowed_origins == None or url.origin() in self.allowed_origins