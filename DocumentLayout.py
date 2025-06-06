from BlockLayout import BlockLayout


maxWidth, HEIGHT = 3400, 2600
HSTEP, VSTEP = 18, 30


class DocumentLayout:
    def __init__(self, node, width, viewSource):
        self.node = node
        self.parent = None
        self.children = []
        self.viewSource=viewSource
        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.maxWidth = width
    

    def layout(self):
        child = BlockLayout(self.node, self, None, self.viewSource)
        self.children.append(child)
        self.width = self.maxWidth - 2*HSTEP
        self.x = HSTEP
        self.y = VSTEP
        child.layout()
        self.height = child.height

    def paint(self):
        return []
