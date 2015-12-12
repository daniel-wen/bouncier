# Progress saving

from fileIO import readFile, writeFile

class Progress(dict):
    attributes = ["score", "time"]
    path = "savefile.txt"

    @staticmethod
    def load():
        # Load from save file
        progress = {}
        for line in readFile(Progress.path).splitlines():
            line = line.split(",")
            level = line[0]
            line = line[1:]
            attributes = {}
            for i, item in enumerate(Progress.attributes):
                if line[i] == "None":
                    attributes[item] = None
                elif line[i].isdecimal():
                    attributes[item] = int(line[i])
                else:
                    attributes[item] = line[i]
            progress[level] = attributes
        return progress

    def __init__(self, levels, game):
        super().__init__(Progress.load())
        self.game = game
        # Fill in missing levels from save file
        for level in levels:
            if level not in self:
                self[level] = dict(zip(Progress.attributes,
                    [None]*len(Progress.attributes)))

    def save(self):
        contents = ""
        for level in self:
            line = level
            for item in Progress.attributes:
                line += "," + str(self[level][item])
            contents += line + "\n"
        writeFile(Progress.path, contents)

    def clear(self):
        for level in self:
            self[level] = dict(zip(Progress.attributes,
                [None]*len(Progress.attributes)))
        self.save()
        self.game.initLevelMenu()
        self.game.menu = self.game.levelMenu
