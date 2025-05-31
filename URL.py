import gzip
import socket
import ssl
from SocketCache import socketCache
from HtmlTimeCache import HtmlTimeCache


class URL:
    def __init__(self, url, htmlCache, connCache):
        self.htmlCache= htmlCache;
        self.connCache = connCache
        self.url = url;
        self.scheme, url = url.split(":", 1);
        if self.scheme == "data":
            self.path = url.split(",", 1)[1];
            return;
        elif self.scheme in ["view-source","about"]:
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
        content = self.htmlCache.get(self.url);
        if content != None:
            print("hi");
            return content;

        s = self.connCache.get(self.url)
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

        self.connCache.add(self.url, s);
        request = f"GET {self.path} HTTP/1.1\r\n"
        request += f"Host: {self.host}\r\n"
        request += f"Connection: {"keep-alive"}\r\n"
        request += f"User-Agent: {"Oh my days"}\r\n"
        request += f"Cache-Control: {"no-store","max-age"}\r\n"
        # request += f"Accept-Encoding: {"gzip"}\r\n"
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

        if (int(status) in [301, 302, 303]):
            redirectUrl = response_headers["location"]
            if redirectUrl[0] == '/':
                print("path", self.host)
                return URL(self.scheme + "://" + self.host + "/" + redirectUrl).request()
            else:
                return URL(redirectUrl).request()


        if "content-length" in response_headers:
            conLen = int(response_headers["content-length"])
            content = response.read(conLen);
            if "content-encoding" in response_headers:
                content = gzip.decompress(content);
        elif "transfer-encoding" in response_headers:
            content = readChunked(s)
            print("content", content)
        
        content = content.decode("utf-8")

        # Should really only cache GET, 200, 301, and 404
        if int(status) == 200 and "cache-control" in response_headers:
            for val in response_headers["cache-control"].split(","):
                if "=" not in val and val[0:6] != "max-age":
                    break;
                else:
                    maxAge = int(val.split("=",1)[1]);
                    self.htmlCache.set(self.url, content, maxAge);

        return content;
    
    
def lex(body):
    in_tag = False;
    i = 0;
    text = ""
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
        elif not in_tag and c != None:
            text += c
        
        i+=1;
    return text;
    
            
def parseHtmlCharRef(cr):
    if cr == "lt":
        return "<";
    elif cr == "gt":
        return ">";

def readChunked(s):
    content = b""
    while True:
        sizeChunk = b""
        while b"\r\n" not in sizeChunk:
            char = s.recv(1)
            if not char: break;
            sizeChunk += char;
        print("sc", sizeChunk)
        line, sizeChunk = sizeChunk.split(b"\r\n", 1)
        chunkSize = int(line.strip(), 16) ;
        print(chunkSize)
        if chunkSize == 0:
            break;

        dataChunk = b"";
        while len(dataChunk) < chunkSize + 2:
            dataChunk += s.read(chunkSize+2 - len(dataChunk));
        content += dataChunk;
        return content;

    
# if __name__ == "__main__":
#     import sys;
#     connCache = socketCache();
#     htmlCache = HtmlTimeCache();
#     if len(sys.argv) <= 1:
#         load(URL("file:///home/robin/Documents/code/WebBrowser/readme.md"))
#     connCache = socketCache();
#     htmlCache = HtmlTimeCache();    load(URL(sys.argv[1]));

#     for value in connCache.cache.values():
#         value.close();

