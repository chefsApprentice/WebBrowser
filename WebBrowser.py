import socket
import ssl

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
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        );
        s.connect((self.host, self.port));
        if (self.scheme == "https"):
            ctx = ssl.create_default_context();
            s = ctx.wrap_socket(s, server_hostname=self.host);
        request = f"GET {self.path} HTTP/1.1\r\n"
        request += f"Host: {self.host}\r\n"
        request += f"Connection: {"close"}\r\n"
        request += f"User-Agent: {"Oh my days"}\r\n"
        request += "\r\n";
        s.send(request.encode("utf8"));
        response = s.makefile("r", encoding="utf8", newline="\r\n");
        statusLine = response.readline();
        version, status, explanation = statusLine.split(" ", 2);
        response_headers = {}
        while True:
            line = response.readline();
            if line == "\r\n": break;
            header, value = line.split(":", 1);
            response_headers[header.casefold()] = value.strip();
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
        content = response.read();
        s.close();
        return content;
    
    
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
    if len(sys.argv) <= 1:
        load(URL("file:///home/robin/Documents/code/WebBrowser/readme.md"))
    else:
        load(URL(sys.argv[1]));
