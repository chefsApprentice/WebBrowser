import re
import tkinter.font
from Tokens import Text, Tag

HSTEP, VSTEP = 18, 30
FONTS = {}

class Layout:
    def __init__(self, tokens, width):
        self.centered = False
        self.width = width
        self.line = []
        self.display_list = []
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size=12
        for tok in tokens:
            self.token(tok);
        self.flush()

    def token(self, tok):
        if isinstance(tok, Text):
            for word in re.findall(r'[^\s\n]+|\n', tok.text):
                self.word(word)
        elif tok.tag == "i":
            self.style="italic"
        elif tok.tag == "/i":
            self.style="roman"
        elif tok.tag == "b":
            self.weight = "bold"
        elif tok.tag == "/b":
            self.weight = "normal"
        elif tok.tag == "small":
            self.size -= 2
        elif tok.tag == "/small":
            self.size += 2
        elif tok.tag == "big":
            self.size += 4
        elif tok.tag == "/big":
            self.size -= 4 
        elif tok.tag == "br":
            self.flush()
        elif tok.tag == "/p":
            self.flush()
            self.cursor_y += VSTEP;
        elif tok.tag == "h1 class=\"title\"":
            self.centered = True;
        elif tok.tag == "/h1" and self.centered:
            self.flush()
            self.centered = False;

                
    def word(self, word):
        font = get_font(self.size, self.weight, self.style)
        w=font.measure(word);
        if self.cursor_x + w > self.width - HSTEP or word == "\n":
            print("word", word)
            if "\N{soft hyphen}" in word:
                word1, word = word.split("\N{soft hyphen}", 1)
                word1 += "-"
                print("w1", word1, "w2", word)
                self.line.append((self.cursor_x, word1, font))
            self.flush()
            self.cursor_x = HSTEP
        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")
        
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
def get_font(size, weight, style):
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight,
            slant=style)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]