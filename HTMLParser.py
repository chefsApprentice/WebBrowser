from Tokens import Text, Element
import sys


# Takes string / body of a file and turns it into a html tree
class HTMLParser:
    # Inits the array of tags which havent been finished (havent been closed)
    def __init__(self, body):
        self.body = body
        self.unfinished = []
    

    # Tags found in the head of html 
    HEAD_TAGS = [
        "base", "basefont", "bgsound", "noscript",
        "link", "meta", "title", "style", "script",
    ]


    # Tags that self close and that the parser eneds to create a clsing tag for.
    SELF_CLOSING_TAGS = [
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    ]
        

    # For each char in body either adds it to a tag or text node, only one node at a time.
    def parse(self):
        i = 0;
        buffer = ""
        inTag = False;
        while i < (len(self.body)):
            c = self.body[i]
            if c == "&":
                cr = self.body[i+1:len(self.body)].split(";", 1)[0]
                htmlParsedC = parseHtmlCharRef(cr)
                if htmlParsedC != None:
                    i += len(cr) + 1;
            if c == "<":
                inTag = True;
                if buffer: self.addText(buffer)
                buffer = ""
            elif c == ">":
                inTag = False;
                self.addTag(buffer)
                buffer = ""
            else:
                buffer += c    

            i+=1;
        if not inTag and buffer:
            self.addText(buffer)
        return self.finish();

    
    # Creates text node
    def addText(self, text):
        if text.isspace(): return
        self.implicitTags(None)
        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)
    

    # Open tag adds to child of previous
    # Close tag adds to end of list with previous as child.
    def addTag(self, tag):
        tag, attributes = self.getAttributes(tag);
        if tag.startswith("!"): return
        self.implicitTags(tag)
        if tag.startswith("/"): 
            if len(self.unfinished) == 1: return
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        elif tag in self.SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            node = Element(tag,attributes, parent)
            parent.children.append(node)
        else:
            parent = self.unfinished[-1] if self.unfinished else None
            if tag == "p" and parent.tag == "p": self.addTag("/p")
            node = Element(tag,attributes, parent)
            self.unfinished.append(node)
    

    # get attributes before creating tag, assumes no spaces and splits on =
    def getAttributes(self, text):
        parts = text.split()
        tag = parts[0].casefold()
        attributes = {}
        for attrPair in parts[1:]:
            if "=" in attrPair:
                key, value = attrPair.split("=", 1)
                if len(value) > 2 and value[0] in ["'", "\""]:
                    value = value[1:-1]
                attributes[key.casefold()] = value
            else:
                attributes[attrPair.casefold()] = ""
        return tag, attributes


    # Finihshes any unclosed tags and then returns the root node of the completed html tree. 
    def finish(self):
        if not self.unfinished:
            self.implicit_tags(None)
        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        return self.unfinished.pop()


    # Tgas that may be omitted are implicit and included in the final html tree. ensures head before body.
    def implicitTags(self, tag):
        while True:
            openTags = [node.tag for node in self.unfinished]
            if openTags == [] and tag != "html":
                self.addTag("html")
            elif openTags == ["html"] and tag not in ["head", "body", "/html"]:
                if tag in self.HEAD_TAGS:
                    self.addTag("head")
                else:
                    self.addTag("body")
            elif openTags == ["html", "head"] and tag not in ["/head"] + self.HEAD_TAGS:
                self.addTag("/head")        
            else:
                break    


# Parse html chars e.g. &lt; Takes in just the part inbetween & and ;
def parseHtmlCharRef(cr):
    if cr == "lt":
        return "<";
    elif cr == "gt":
        return ">";


# Prints the html tree in an indendted way to show children
def printTree(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        printTree(child, indent + 2)