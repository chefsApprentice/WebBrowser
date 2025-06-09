from Tokens import Element 
from TagSelector import TagSelector
from DescendantSelector import DescendantSelector


INHERITED_PROPERTIES = {
    "font-size": "16px",
    "font-style": "normal",
    "font-weight": "normal",
    "color": "black",
}


class CSSParser:
    def __init__(self, s):
        self.s = s
        self.i = 0

    # Skips all the whitespace 
    def whitespace(self):
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1
    

    # Returns a parsed word (prop or val doesnt matter)
    def word(self):
        start = self.i
        while self.i < len(self.s):
            if self.s[self.i].isalnum() or self.s[self.i] in "#-.%":
                self.i += 1
            else:
                break
        if not (self.i > start):
            raise Exception("Parsing error")
        return self.s[start:self.i]

    
    # verifies if the current char is a literal as it should be e.g. colon
    def literal(self, literal):
        if not (self.i < len(self.s) and self.s[self.i] == literal):
            raise Exception("Parsing error")
        self.i += 1


    # Returns a single pair of properties and values from the word
    def pair(self):
        prop = self.word()
        self.whitespace()
        self.literal(":")
        self.whitespace()
        val = self.word()
        return prop.casefold(), val
    

    # gets style attributes as a sequence of pairs
    def body(self):
        pairs = {}
        while self.i < len(self.s) and self.s[self.i] != "}":
            # Postels Law = allow minimally confroming input
            try:
                prop, val = self.pair()
                pairs[prop.casefold()] = val
                self.whitespace()
                self.literal(";")
                self.whitespace()
            except Exception:
                why = self.ignoreUntil([";"])
                if why == ";":
                    self.literal(";")
                    self.whitespace
                else: 
                    break;
        return pairs


    # Stops until it reaches non whitespace char or eof and returns that char.
    def ignoreUntil(self, chars):
        while self.i < len(self.s):
            if self.s[self.i] in chars:
                return self.s[self.i]
            else:
                self.i += 1
        return None


    # Gets the correct selector, (tag or descendant)
    def selector(self):
        out = TagSelector(self.word().casefold())
        self.whitespace()
        while self.i < len(self.s) and self.s[self.i] != "{":
            tag = self.word()
            descendant = TagSelector(tag.casefold())
            out = DescendantSelector(out, descendant)
            self.whitespace()
        return out


    # Parse a css file as a series of selector bracket atrributes/rules.
    def parse(self):
        rules = []
        while self.i < len(self.s):
            try:
                self.skipComments()
                self.whitespace()
                selector = self.selector()
                self.literal("{")
                self.whitespace()
                body = self.body()
                self.literal("}")
                rules.append((selector, body))
            except Exception:
                why = self.ignoreUntil(["}"])
                if why == "}":
                    self.literal = "}"
                    self.whitespace()
                    self.i+=1
                else:
                    break;
        return rules
    

    # Increase i if start = /* until reaches */
    def skipComments(self):
        print("skipCom:" , "i", self.i , "len", len(self.s))
        if self.i < len(self.s) - 1 and self.s[self.i:self.i+2] != "/*": return;
        print("skip1")
        while self.i < len(self.s) - 1:
            print("skip2")
            if self.s[self.i:self.i+2] == "*/":
                self.i+=2;
                return;
            self.i += 1

        

# Sets the style for a node based on the rules, creates the nodes style property.
def style(node, rules):
    node.style = {}
    # Inherited properties should go first as should be overwritten.
    for prop, defaultVal in INHERITED_PROPERTIES.items():
        if node.parent:
            node.style[prop] = node.parent.style[prop]
        else:
            node.style[prop] = defaultVal
    # Apply general rules
    for selector, body in rules:
        if not selector.matches(node): continue;
        for prop, value in body.items():
            node.style[prop] = value
    # Apply attributes specified for that specific node in style attribute
    if isinstance(node, Element) and "style" in node.attributes:
        pairs = CSSParser(node.attributes["style"]).body();
        for prop, value in pairs.items():
            node.style[prop] = value
    # Turn percentage font size into computed value
    if node.style["font-size"].endswith("%"):
        if node.parent: parentFontSize = node.parent.style["font-size"]
        else: parentFontSize = INHERITED_PROPERTIES["font-size"]
        nodePerc = float(node.style["font-size"][:-1]) / 100
        parentPx = float(parentFontSize[:-2])
        node.style["font-size"] = str(nodePerc * parentPx) + "px"
    # Style children
    for child in node.children:
        style(child, rules)



# Get cascade priority from rule. Used for comparison.
def cascadePriority(rule):
    selector, body = rule
    return selector.priority