import tkinter as tk
from HtmlTimeCache import HtmlTimeCache
from SocketCache import socketCache
from URL import URL, lex


width, height = 3400, 2600
HSTEP, VSTEP = 18, 30
SCROLL_STEP = 100



class Browser:
    def __init__(self):
        self.connCache = socketCache();
        self.htmlCache = HtmlTimeCache();
        self.scroll = 0;
        self.window = tk.Tk()
        self.window.resizable(True, True)
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.touchpadScroll)
        self.window.bind("<Configure>", self.resize)
        self.canvas = tk.Canvas(
            self.window, 
            width=width,
            height=height
        )
        self.canvas.pack(fill="both",expand=True)

    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + height: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y-self.scroll, text=c)
 
    def load(self, url):
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

        self.text = lex(body);
    
        self.display_list = layout(self.text)
        self.draw()


    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollup(self, e):
        if (self.scroll-SCROLL_STEP >= 0):
            self.scroll -= SCROLL_STEP
            self.draw()
    
    def touchpadScroll(self, e):
        print(e)

    def resize(self ,e):
        global width, height
        width = e.width
        height = e.height
        self.canvas.config(width=width, height=height)
        self.display_list = layout(self.text);
        self.draw();


def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        cursor_x += HSTEP
        if cursor_x > width - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP
        elif c == "\n":
            cursor_y += VSTEP
            cursor_x = HSTEP
        display_list.append((cursor_x, cursor_y, c))
    return display_list



if __name__ == "__main__":
    import sys; 
    browser = Browser();
    if len(sys.argv) <= 1:
        browser.load(URL("file:///home/robin/Documents/code/WebBrowser/readme.md", browser.htmlCache, browser.connCache))
    else:
        browser.load(URL(sys.argv[1], browser.htmlCache, browser.connCache));
    tk.mainloop()