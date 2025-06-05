import re
import tkinter.font
from Tokens import Text, Element

HSTEP, VSTEP = 18, 30
FONTS = {}

# Handles the positioning and styling of text given a html tree.
# Caches font for massive performance benefit.
class Layout:
    # Sets the default styling variables and creates a display list of text.
    def __init__(self, tree, width, viewSource=False):
        self.centered = False
        self.width = width
        self.line = []
        self.display_list = []
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size=12
        self.viewSource = viewSource
        if viewSource:
            self.weight = "bold"
            self.viewSourceRecurse(tree)
        else:
            self.recurse(tree)
        self.flush()

    # Goes through tokens and makes appropriate changes to display list / styling.
    def recurse(self, tree):
        if isinstance(tree, Text):
            for word in re.findall(r'[^\s\n]+|\n', tree.text):
                self.word(word)
        else:
            self.openTag(tree.tag)
            for child in tree.children:
                self.recurse(child)
            self.closeTag(tree.tag)
    
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
    def word(self, word):
        font = getFont(self.size, self.weight, self.style)
        w=font.measure(word);
        if self.cursor_x + w > self.width - HSTEP or word == "\n":
            if "\N{soft hyphen}" in word:
                word1, word = word.split("\N{soft hyphen}", 1)
                word1 += "-"
                self.line.append((self.cursor_x, word1, font))
            self.flush()
            self.cursor_x = HSTEP
        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")
    

    # Goes through the current line that and alligns the text to all have the same baseline, adds line to display list.
    def flush(self):
        # Align / find baseline
        if not self.line: return;
        metrics = [font.metrics() for x, word, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1 * max_ascent
        if self.centered: baseline_x = (self.width / 2) - ((self.cursor_x - HSTEP) / 2)
        # Add all words to display list
        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            if self.centered: x += baseline_x
            self.display_list.append((x,y,word,font));
        # Update cursor_x, y fields
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1 * max_descent
        self.cursor_x = HSTEP
        # Flush
        self.line=[]

# Gets a font or creates one, used for cacheing and optimisation
def getFont(size, weight, style):
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight,
            slant=style)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]