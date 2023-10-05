import socket
import ssl
from text import Text
from element import Element

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

        
    def request(self):
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
        
        s.send((f"GET {self.path} HTTP/1.0\r\n" + \
                f"Host: {self.host}\r\n\r\n") \
               .encode("utf8"))
        
        # Read and interpret response from host
        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        assert status == "200", f"{status}: {explanation}"
        
        # Map headers
        headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            headers[header.lower()] = value.strip()
        
        # Check if unique headers are not present
        assert "transfer-encoding" not in headers
        assert "content-encoding" not in headers
        
        body = response.read()
        s.close()
        return headers, body
