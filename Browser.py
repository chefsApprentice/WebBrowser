import tkinter as tk
from HtmlTimeCache import HtmlTimeCache
from SocketCache import socketCache
from URL import URL
from HTMLParser import HTMLParser, printTree
from DocumentLayout import DocumentLayout
from BlockLayout import paintTree
from Tokens import Text


width, height = 3400, 2600
HSTEP, VSTEP = 18, 30
SCROLL_STEP = 100



# Browser component which handles passing data between classes and rendering the pages.
class Browser:
    # Init class handling keyboard bindings, creating the canvas and creating the caches.
    def __init__(self):
        self.connCache = socketCache();
        self.htmlCache = HtmlTimeCache();
        self.viewSource = False;
        self.scroll = 0;
        self.window = tk.Tk()
        self.window.resizable(True, True)
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        # self.window.bind("<MouseWheel>", self.touchpadScroll) # Used for scrolling with a mouse
        self.window.bind("<Configure>", self.resize)
        self.canvas = tk.Canvas(
            self.window, 
            width=width,
            height=height
        )
        self.canvas.pack(fill="both",expand=True)


    # Draws text to canvas using tkinter text
    def draw(self):
        self.canvas.delete("all")
        for cmd in self.displayList:
            if cmd.top > self.scroll + height: continue
            if cmd.bottom < self.scroll: continue
            cmd.execute(self.scroll, self.canvas)
        
        # Scroll indiicator showing position throughout text
        
        totalHeight = self.document.height + 2*VSTEP - height
        if totalHeight < height: return
        scrollPerc = self.scroll / totalHeight * height
        minScroll = scrollPerc
        maxScroll = scrollPerc+40
        if (scrollPerc == 0):
            minScroll = 0
            maxScroll = scrollPerc+40
        elif (scrollPerc+40 >= height):
            minScroll = height-40
            maxScroll = height
        self.canvas.create_rectangle(width-20, minScroll, width, maxScroll , fill="blue")
 

    # Loads the file based on scheme, then calls necessary functions needed to render. 
    def load(self, url):
        if url.scheme == "file":
            with open(url.path) as f:
                body = f.read();
        elif url.scheme == "data":
            body = url.path;
        elif url.scheme == "view-source":
            body = URL(url.path, self.htmlCache, self.connCache).request()
            self.viewSource=True;
        elif url.scheme == "about":
            if url.path == "blank": body = " "
        else:
            body = url.request();

        self.nodes = HTMLParser(body).parse();
        self.document = DocumentLayout(self.nodes, width, self.viewSource)
        self.document.layout();
        self.displayList = []
        paintTree(self.document, self.displayList)
        self.draw()


    # On scrolldown move scroll posiiton and rerender
    def scrolldown(self, e):
        maxY = max(self.document.height + 2*VSTEP - height, 0) 
        if (self.scroll+SCROLL_STEP < maxY):
            self.scroll += SCROLL_STEP
            self.draw()

    # On scrollup move and redraw
    def scrollup(self, e):
        if (self.scroll-SCROLL_STEP >= 0):
            self.scroll -= SCROLL_STEP
            self.draw()

    # Updates layout and redraws on resizing of windows.
    def resize(self ,e):
        global width, height
        width = e.width
        height = e.height
        self.canvas.config(width=width, height=height)
        self.document = DocumentLayout(self.nodes, width, self.viewSource)
        self.document.layout(); 
        self.displayList = []
        paintTree(self.document, self.displayList)
        self.draw();



# Main function to call the browser with a url or load a default page.
if __name__ == "__main__":
    import sys; 
    browser = Browser();
    if len(sys.argv) <= 1:
        browser.load(URL("file:///home/robin/Documents/code/WebBrowser/readme.md", browser.htmlCache, browser.connCache))
    else:
        # try:
        browser.load(URL(sys.argv[1], browser.htmlCache, browser.connCache));
        # except:
        #     browser.load(URL("about:blank", browser.htmlCache, browser.connCache));

    tk.mainloop()