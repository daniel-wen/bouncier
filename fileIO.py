# File IO functions from course notes
# http://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO

def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)
