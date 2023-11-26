import socket
import ssl
from text import Text
from element import Element


COOKIE_JAR = {}

class URL:
    
    def __init__(self, url: str):
        
        self.scheme = str
        self.host = str
        self.path = str
        self.port = int
        
        # Extract the scheme from given url
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"], \
            "Unknown scheme {}".format(self.scheme)
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443
            
        # Extract host and path from url
        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url
        
        # Optional custom port (https://example.org:8080/index.html)
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

        
    def request(self, top_level_url, payload=None):
        # Connect to the host
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        s.connect((self.host, self.port))
        
        # Wrap socket with encryption
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)
        
        # Decide between GET and POST request
        method = "POST" if payload else "GET"
        
        body = f"{method} {self.path} HTTP/1.0\r\n"
        
        # Send cookie to site
        if self.host in COOKIE_JAR:
            cookie, params = COOKIE_JAR[self.host]
            allow_cookie = True
            if top_level_url and params.get("samesite", "none") == "lax":
                if method != "GET":
                    allow_cookie = self.host == top_level_url.host
            if allow_cookie:
                body += f"Cookie: {cookie}\r\n"
        
        if payload:
            length = len(payload.encode("utf8"))
            body += f"Content-Length: {length}\r\n"
            body += "\r\n" + (payload if payload else "")
        else:
            body += f"Host: {self.host}\r\n\r\n"
        
        s.send(body.encode("utf8"))
        
        # Read and interpret response from host
        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        assert status == "200", f"{status}: {explanation}"
        
        # Map headers
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.lower()] = value.strip()
            
        # Update cookies if told to
        if "set-cookie" in response_headers:
            cookie = response_headers["set-cookie"]
            params = {}
            if ";" in cookie:
                cookie, rest = cookie.split(";", 1)
                for param in rest.split(";"):
                    if '=' in param:
                        param, value = param.strip().split("=", 1)
                    else:
                        value = "true"
                    params[param.casefold()] = value.casefold()
            COOKIE_JAR[self.host] = (cookie, params)
        
        # Check if unique headers are not present
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
        
        body = response.read()
        s.close()
        return response_headers, body
    
    def resolve(self, url):
        if "://" in url: return URL(url)
        if not url.startswith("/"):
            dir, _ = self.path.rsplit("/", 1)
            while url.startswith("../"):
                _, url = url.split("/", 1)
                if "/" in dir:
                    dir, _ = dir.rsplit("/", 1)
            url = dir + "/" + url
        return URL(self.scheme + "://" + self.host + \
                   ":" + str(self.port) + url)
        
    def origin(self):
        return self.scheme + "://" + self.host + ":" + str(self.port)

    def __str__(self):
        port_part = ":" + str(self.port)
        if self.scheme == "https" and self.port == 443:
            port_part = ""
        if self.scheme == "http" and self.port == 80:
            port_part = ""
        return self.scheme + "://" + self.host + port_part + self.path
