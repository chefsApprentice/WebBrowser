# Token html node that represents a piece of text
class Text:
    def __init__(self, text, parent):
        self.text = text
        self.children = []
        self.parent = parent
    def __repr__(self):
        return repr(self.text)
    
# Token html node that represents a tag element and attributes e.g. div h=5
class Element:
    def __init__(self, tag, attributes, parent):
        self.tag = tag
        self.children = []
        self.attributes = attributes
        self.parent = parent
    def __repr__(self):
        return "<" + self.tag + ">"