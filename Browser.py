import tkinter as tk
from HtmlTimeCache import HtmlTimeCache
from SocketCache import socketCache
from URL import URL, lex


WIDTH, HEIGHT = 3400, 2600
HSTEP, VSTEP = 18, 30
SCROLL_STEP = 100



class Browser:
    def __init__(self):
        self.connCache = socketCache();
        self.htmlCache = HtmlTimeCache();
        self.scroll = 0;
        self.window = tk.Tk()
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.touchpadScroll)
        self.canvas = tk.Canvas(
            self.window, 
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()

    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + HEIGHT: continue
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

        text = lex(body);
    
        self.display_list = layout(text)
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


def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP

        if c == "\n":
            cursor_y += 2* HSTEP
            cursor_x = HSTEP
        elif cursor_x >= WIDTH - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP
    return display_list



if __name__ == "__main__":
    import sys; 
    browser = Browser();
    if len(sys.argv) <= 1:
        browser.load(URL("file:///home/robin/Documents/code/WebBrowser/readme.md", browser.htmlCache, browser.connCache))
    else:
        browser.load(URL(sys.argv[1], browser.htmlCache, browser.connCache));
    tk.mainloop()