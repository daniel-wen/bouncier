# Map loading

from terrain import *
from fileIO import readFile

class Maps(object):
    def __init__(self, left, top, width, height):
        path = "maps.txt"
        self.left = left
        self.top = top
        self.width = width
        self.height = height

        self.maps = {}
        # Sequence of levels may not all be integers
        self.levels = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                     "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]
        # Load maps from file into list
        for line in readFile(path).splitlines():
            if line == "" or line.startswith("#"):
                # Skip blank lines or comments
                continue
            elif line.startswith("map"):
                # Map data begins
                mapName = line.split(" ")[1]
                mapData = []
            elif line.startswith("end"):
                # Map data ends
                self.maps[mapName] = mapData
            else:
                # Load map data
                mapData.append(list(line))

    def load(self, mapName):
        # Load terrain elements according to map
        mapData = self.maps[mapName]
        rows = len(mapData)
        cols = len(mapData[0])
        # Make sizes fit the window
        self.cellSize = min(self.width//cols, self.height//rows)
        terrainElements = []
        for i in range(rows):
            for j in range(cols):
                x = self.left + j*self.cellSize
                y = self.top + i*self.cellSize
                code = mapData[i][j]
                if code == "s":
                    # Starting position of ball
                    startx = x + self.cellSize//2
                    starty = y + self.cellSize//2
                elif code != "-":
                    # Not an empty space
                    Element = Terrain.getClassFromCode(code)
                    element = Element(x, y, self.cellSize, self.cellSize)
                    terrainElements.append(element)
        return terrainElements, (startx, starty)
