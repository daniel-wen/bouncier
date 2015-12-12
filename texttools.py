# Menu and text tools

DIRECTIONS = {"nw", "n", "ne", "w", "c", "e", "sw", "s", "se"}

def drawText(screen, x, y, text="", font=None, anchor="c", color=(0,0,0)):
    # Tkinter-style text helper
    if text == "" or font == None or anchor not in DIRECTIONS:
        assert(False)
    textSurface = font.render(text, True, color)
    rect = textSurface.get_bounding_rect()
    # Get left position
    if anchor in ("nw", "w", "sw"):
        left = x
    elif anchor in ("n", "c", "s"):
        left = x - rect.width//2
    elif anchor in ("ne", "e", "se"):
        left = x - rect.width
    # Get top position
    if anchor in ("nw", "n", "ne"):
        top = y
    elif anchor in ("w", "c", "e"):
        top = y - rect.height//2
    elif anchor in ("sw", "s", "se"):
        top = y - rect.height
    # Draw the text
    screen.blit(textSurface, (left, top))
    return x + rect.width

# For creating menus
class Menu(object):
    def __init__(self, x, y, entries, actions):
        self.x = x
        self.y = y
        self.entries = entries
        self.actions = actions
        self.selected = 0
        self.lineHeight = 24

    def key(self, keyCode):
        if keyCode == 273:
            # Up
            self.selected -= 1
            if self.selected < 0:
                self.selected = len(self.entries) - 1
        elif keyCode == 274:
            # Down
            self.selected += 1
            if self.selected == len(self.entries):
                self.selected = 0
        elif keyCode == 13:
            # Enter
            function = self.actions[self.selected]
            if function != None:
                result = function()
                if result == "sound on":
                    self.entries[self.selected] = "Turn sound off"
                elif result == "sound off":
                    self.entries[self.selected] = "Turn sound on"

    def draw(self, screen, font):
        space = 20
        maxRows = 12
        rowWidth = 325
        for i, text in enumerate(self.entries):
            col = i // maxRows
            row = i % maxRows
            left = self.x + col*rowWidth
            top = self.y + row*self.lineHeight
            drawText(screen, left + space, top, text=text, font=font,
                anchor="nw")
            if i == self.selected:
                # Draw the selector
                drawText(screen, left, top, text=">", font=font, anchor="nw")
