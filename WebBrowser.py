import socket
import ssl
from collections import OrderedDict;

class socketCache:
    def __init__(self, maxSize = 1):
        self.maxSize=maxSize;
        self.cache = OrderedDict();

    def get(self, key):
        return self.cache.get(key);

    def add(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key);
        self.cache[key] = value;
        if len(self.cache) > self.maxSize:
            key2, val = self.cache.popitem(last=False)
            val.close();


class URL:
    def __init__(self, url):
        self.scheme, url = url.split(":", 1);
        if self.scheme == "data":
            self.path = url.split(",", 1)[1];
            return;
        elif self.scheme == "view-source":
            self.path = url;
            return;

        __, url = url.split("//", 1);
        if self.scheme == "file":
            self.path = url;
            return;

        assert self.scheme in ["http","https"];
        if self.scheme == "http":
            self.port = 80;
        elif self.scheme == "https":
            self.port = 443;    

        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1);
        if ":" in self.host:
            self.host, self.port = self.host.split(":", 1);
            self.port = int(self.port);
        self.path = "/" + url;
        
        
    def request(self):
        s = connCache.get(self.path)
        if (s == None):
            s = socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP,
            );
            s.connect((self.host, self.port));
            if (self.scheme == "https"):
                ctx = ssl.create_default_context();
                s = ctx.wrap_socket(s, server_hostname=self.host);

        connCache.add(self.path, s);
        request = f"GET {self.path} HTTP/1.1\r\n"
        request += f"Host: {self.host}\r\n"
        request += f"Connection: {"keep-alive"}\r\n"
        request += f"User-Agent: {"Oh my days"}\r\n"
        request += "\r\n";
        s.send(request.encode("utf8"));
        response = s.makefile("rb");
        statusLine = response.readline().decode("utf-8").strip();
        version, status, explanation = statusLine.split(" ", 2);

        response_headers = {}
        while True:
            line = response.readline().decode("utf-8")
            if line in ('\r\n', '\n', ''): break;
            header, value = line.split(":", 1);
            response_headers[header.casefold()] = value.strip();
            print(header.casefold(), response_headers[header.casefold()])

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        if (int(status) in [301, 302, 303]):
            redirectUrl = response_headers["location"]
            if redirectUrl[0] == '/':
                print("path", self.host)
                return URL(self.scheme + "://" + self.host + "/" + redirectUrl).request()
            else:
                return URL(redirectUrl).request()

        conLen = int(response_headers["content-length"])
        content = response.read(conLen);
        return content.decode("utf-8");
    
    
def show(body):
    in_tag = False;
    i = 0;
    while i < (len(body)):
        c = body[i]
        if c == "&":
            cr = body[i+1:len(body)].split(";", 1)[0]
            c = parseHtmlCharRef(cr);
            i += len(cr) + 1;
        if c == "<":
            in_tag = True;
        elif c == ">":
            in_tag = False;
        elif not in_tag:
            print(c, end="");
        
        i+=1;
    
            
def load(url):
    if url.scheme == "file":
        with open(url.path) as f:
            body = f.read();
    elif url.scheme == "data":
        body = url.path;
    elif url.scheme == "view-source":
        body = URL(url.path).request();
        print(body);
        return;
    else:
        body = url.request();
    show(body);
    

def parseHtmlCharRef(cr):
    if cr == "lt":
        return "<";
    elif cr == "gt":
        return ">";
    
if __name__ == "__main__":
    import sys;
    connCache = socketCache();
    if len(sys.argv) <= 1:
        load(URL("file:///home/robin/Documents/code/WebBrowser/readme.md"))
    else:
        load(URL(sys.argv[1]));

    for value in connCache.cache.values():
        value.close();

