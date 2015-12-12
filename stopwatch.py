# Timer functions

class Stopwatch(object):
    second = 1000

    @staticmethod
    def secToMin(n):
        mod = 60
        n = round(n)
        minutes = n // mod
        seconds = n % mod
        minOnes = minutes % 10
        minTens = minutes // 10
        secOnes = seconds % 10
        secTens = seconds // 10
        return "%d%d:%d%d" % (minTens, minOnes, secTens, secOnes)

    def __init__(self):
        self.ms = 0
        self.running = False

    def __str__(self):
        return Stopwatch.secToMin(self.getSeconds())

    def tick(self, dt):
        if self.running:
            self.ms += int(dt)

    def pause(self):
        self.running = False

    def go(self):
        self.running = True

    def restart(self):
        self.ms = 0
        self.go()

    def getSeconds(self):
        return self.ms//Stopwatch.second
