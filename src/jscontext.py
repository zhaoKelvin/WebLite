import dukpy
from cssparser import CSSParser
from element import Element
from htmlparser import HTMLParser
from utils import tree_to_list


RUNTIME_JS = open("runtime.js").read()
EVENT_DISPATCH_JS = "new Node(dukpy.handle).dispatchEvent(new Event(dukpy.type))"


class JSContext:
    def __init__(self, tab):
        self.tab = tab
        self.node_to_handle = {}
        self.handle_to_node = {}
        
        self.interp = dukpy.JSInterpreter()
        self.interp.export_function("log", print)
        self.interp.export_function("querySelectorAll", self.querySelectorAll)
        self.interp.export_function("getAttribute", self.getAttribute)
        self.interp.export_function("innerHTML_set", self.innerHTML_set)
        self.interp.export_function("XMLHttpRequest_send", self.XMLHttpRequest_send)
        self.interp.evaljs(RUNTIME_JS)

    def run(self, code):
        return self.interp.evaljs(code)

    def querySelectorAll(self, selector_text):
        selector = CSSParser(selector_text).selector()
        
        nodes = [node for node in tree_to_list(self.tab.nodes, []) if selector.matches(node)]
        return [self.get_handle(node) for node in nodes]
    
    def get_handle(self, elt):
        if elt not in self.node_to_handle:
            handle = len(self.node_to_handle)
            self.node_to_handle[elt] = handle
            self.handle_to_node[handle] = elt
        else:
            handle = self.node_to_handle[elt]
        return handle

    def getAttribute(self, handle, attr):
        elt = self.handle_to_node[handle]
        return elt.attributes.get(attr, None)
    
    def dispatch_event(self, type, elt):
        handle = self.node_to_handle.get(elt, -1)
        do_default = self.interp.evaljs(EVENT_DISPATCH_JS, type=type, handle=handle)
        return not do_default
        
    def innerHTML_set(self, handle, s):
        doc = HTMLParser("<html><body>" + s + "</body></html>").parse()
        new_nodes = doc.children[0].children
        elt: Element = self.handle_to_node[handle]
        elt.children = new_nodes
        for child in elt.children:
            child.parent = elt
        self.tab.render()

    def XMLHttpRequest_send(self, method, url, body):
        full_url = self.tab.url.resolve(url)
        if not self.tab.allowed_request(full_url):
            raise Exception("Cross-origin XHR blocked by CSP")
        if full_url.origin() != self.tab.url.origin():
            raise Exception("Cross-origin XHR request not allowed")
        headers, out = full_url.request(self.tab.url, body)
        return out
