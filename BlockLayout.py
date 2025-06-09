import re
import tkinter.font
from Tokens import Text, Element
from DrawText import DrawText
from DrawRect import DrawRect


HSTEP, VSTEP = 18, 30
FONTS = {}

BLOCK_ELEMENTS = [
    "html", "body", "article", "section", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
    "footer", "address", "p", "hr", "pre", "blockquote",
    "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
    "figcaption", "main", "div", "table", "form", "fieldset",
    "legend", "details", "summary"
]

# Handles the positioning and styling of text given a html tree.
# Caches font for massive performance benefit.
class BlockLayout:
    # Sets the default styling variables and creates a display list of text.
    def __init__(self, node, parent, previous, viewSource=False):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []
        self.viewSource = viewSource
        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.displayList = []

    def layout(self):
        if isinstance(self.node, Element) and self.node.tag == "head":
            self.height = 0
            return

        self.x = self.parent.x
        self.width = self.parent.width
        if self.previous and self.previous.y:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        mode = self.layoutMode()
        if mode == "block":
            previous = None
            inBody = False;
            for child in self.node.children:
                if isinstance(child, Element) and child.tag == "body": inBody = True
                if isinstance(self.node, Element) and self.node.tag == "html" and not inBody: continue;
                nextChild = BlockLayout(child, self, previous)
                self.children.append(nextChild)
                previous = nextChild
        else:
            self.cursor_x = 0
            self.cursor_y = 0
            self.centered = False
            self.weight = "normal"
            self.style = "roman"
            self.size=12
            self.line = []
            if self.viewSource:
                self.weight = "bold"
                self.viewSourceRecurse(self.node)
            else:
                self.recurse(self.node)
            self.flush()


        # print("self", self.node.tag)

        for child in self.children:
            child.layout()

        if mode =="block":
            self.height = sum([child.height for child in self.children])
        else: 
            self.height = self.cursor_y


    def layoutMode(self):
        if isinstance(self.node, Text):
            return "inline"
        elif any([isinstance(child, Element) and \
                  child.tag in BLOCK_ELEMENTS
                  for child in self.node.children]):
            return "block"
        elif self.node.children:
            return "inline"
        else:
            return "block"

    
    # Node children = html tree, creates layout tree in self.children``
    # def layoutIntermediate(self):
    #     previous = None;
    #     for child in self.node.chidlren:
    #         nextBlock = BlockLayout(child, self, previous)
    #         self.children.append(nextBlock)
    #         previous = nextBlock


    # Goes through tokens and makes appropriate changes to display list / styling.
    def recurse(self, node):
        if isinstance(node, Text):
            for word in re.findall(r'[^\s\n]+|\n', node.text):
                self.word(node, word)
        else:
            self.openTag(node.tag)
            for child in node.children:
                self.recurse(child)
            self.closeTag(node.tag)
    
    def viewSourceRecurse(self, tree):
        if isinstance(tree, Text):
            self.weight = "normal"
            for word in re.findall(r'[^\s\n]+|\n', tree.text):
                self.word(word)
            self.weight = "bold"
        else:
            self.flush()
            self.word("<"+tree.tag+">")
            self.flush()
            for child in tree.children:
                self.viewSourceRecurse(child)
            self.flush()
            self.word("</"+tree.tag+">")

    # Looks at content inside Open tag '<',and changes style accordingly based on element.
    def openTag(self, tag):
        if tag == "i": self.style = "italic"
        elif tag == "b": self.weight = "bold"
        elif tag == "small": self.size -= 2;
        elif tag == "big": self.size += 4
        elif tag == "br": self.flush();
        elif tag == "h1 class=\"title\"": self.centered = True;
    

    # Looks at content inside Close tag '>',and changes style to default.
    def closeTag(self, tag):        
        if tag == "i": self.style = "roman"
        elif tag == "b": self.weight = "normal"
        elif tag == "small": self.size += 2;
        elif tag == "big": self.size -= 4;
        elif tag == "p": 
            self.flush();   
            self.cursor_y += VSTEP
        elif tag == "h1" and self.centered:
            self.flush()
            self.centered = False

                
    # Takes a word and checks wether it fits on the current line. Adds word to current line at proper position.
    def word(self, node, word):
        weight = node.style["font-weight"]
        style = node.style["font-style"]
        color = node.style["color"]
        if style == "normal": style = "roman"
        # Convert from px to tk points
        size = int(float(node.style["font-size"][:-2]) * .75)
        font = getFont(size, weight, style)
        w=font.measure(word);
        if self.cursor_x + w > self.width or word == "\n":
            if "\N{soft hyphen}" in word:
                word1, word = word.split("\N{soft hyphen}", 1)
                word1 += "-"
                self.line.append((self.cursor_x, word1, font, color))
            self.flush()
            self.cursor_x = HSTEP
        self.line.append((self.cursor_x, word, font, color))
        self.cursor_x += w + font.measure(" ")
    

    # Goes through the current line that and alligns the text to all have the same baseline, adds line to display list.
    def flush(self):
        # Align / find baseline
        if not self.line: return;
        metrics = [font.metrics() for x, word, font, color in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1 * max_ascent
        if self.centered: baseline_x = (self.width / 2) - ((self.cursor_x - HSTEP) / 2)
        # Add all words to display list
        for relX, word, font, color in self.line:
            x = self.x + relX
            y = self.y + baseline - font.metrics("ascent")
            if self.centered: x += baseline_x
            self.displayList.append((x,y,word,font, color));
        # Update cursor_x, y fields
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1 * max_descent
        self.cursor_x = 0
        # Flush
        self.line=[]
    

    def paint(self):
        cmds = []
        if isinstance(self.node, Element) and self.node.tag == "pre":
            x2,y2, = self.x +self.width, self.y + self.height
            cmds.append(DrawRect(self.x, self.y, x2, y2, "gray") )
        elif isinstance(self.node, Element) and self.node.tag == "nav":
            x2,y2, = self.x +self.width, self.y + self.height
            cmds.append(DrawRect(self.x, self.y, x2, y2, "light steel blue") )
       
        bgColour = self.node.style.get("background-color", "transparent")
        if bgColour != "transparent":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = DrawRect(self.x, self.y, x2, y2, bgColour)
            cmds.append(rect)

        if self.layoutMode() == "inline":
            for x, y, word, font, color in self.displayList:
                cmds.append(DrawText(x,y, word, font, color))        
        
        return cmds 



def paintTree(layoutObject, displayList):
    displayList.extend(layoutObject.paint())
    for child in layoutObject.children:
        paintTree(child, displayList)    


# Gets a font or creates one, used for cacheing and optimisation
def getFont(size, weight, style):
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight,
            slant=style)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]