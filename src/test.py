import sys
from htmlparser import HTMLParser, print_tree
from url import URL


headers, body = URL(sys.argv[1]).request()
nodes = HTMLParser(body).parse()
print_tree(nodes)
