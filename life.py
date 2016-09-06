import collections

import time

import sys

import select

import os

Cell = collections.namedtuple("Cell", "x y")

class LifeGrid:
  SEED_LIST = "list"
  SEED_IMAGE = "image"

  def __init__(self, width=-1, height=-1, seedFile="seed.txt", seedFormat=SEED_LIST):
    self.liveCells = [Cell(x=1, y=1),
                      Cell(x=1, y=2),
                      Cell(x=1, y=3),]
    self.liveCells = self.parseSeedFile(seedFile, seedFormat)
    self.step = 0

    self.deadCellChar = "_"
    self.liveCellChar = "O"

    self.width = width
    self.height = height

  def parseSeedFile(self, seedFile, seedFormat):
    liveCells = []
    with open(seedFile, "r") as seed:
      for lineIndex, line in enumerate(seed):
        print "Processing line: '{}'".format(line)
        for charIndex, character in enumerate(line):
          if character == "*":
            liveCells.append(Cell(x=charIndex, y=lineIndex))
    return liveCells

  def getNeighbors(self, cell):
    x = cell[0]
    y = cell[1]
    yield Cell(x=x-1, y=y-1)
    yield Cell(x=x,   y=y-1)
    yield Cell(x=x+1, y=y-1)
    yield Cell(x=x-1, y=y  )
    yield Cell(x=x+1, y=y  )
    yield Cell(x=x-1, y=y+1)
    yield Cell(x=x,   y=y+1)
    yield Cell(x=x+1, y=y+1)

  def getLiveNeighborNum(self, cell, liveCells, maxNeighbors=4):
    neighborCount = 0
    for neighbor in self.getNeighbors(cell):
      if neighbor in liveCells:
        neighborCount += 1
      if neighborCount >= maxNeighbors:
        break
    return neighborCount

  def tick(self):
    newLiveCells = []
    liveCellsToProcess = list(self.liveCells)
    deadCellsToProcess = []
   
    # Populate deadCellsToProcess 
    for cell in self.liveCells:
      [deadCellsToProcess.append(neighbor) for neighbor in self.getNeighbors(cell) if(neighbor not in self.liveCells and neighbor not in deadCellsToProcess)]

    for cell in liveCellsToProcess:
      if (self.width > 0 and cell[0] > self.width) or (self.height > 0 and cell[1] > self.height) or (cell[1] < 0) or (cell[0] < 0):
        continue
      liveNeighbors = self.getLiveNeighborNum(cell, self.liveCells)
      if liveNeighbors == 2 or liveNeighbors == 3:
        newLiveCells.append(cell)
    for cell in deadCellsToProcess:
      if (self.width > 0 and cell[0] > self.width) or (self.height > 0 and cell[1] > self.height) or (cell[1] < 0) or (cell[0] < 0):
        continue
      liveNeighbors = self.getLiveNeighborNum(cell, self.liveCells)
      if liveNeighbors == 3:
        newLiveCells.append(cell)

    self.liveCells = newLiveCells
    
    self.step += 1

  def clearGrid(self, width, height):
    os.system("clear")

  def printGrid(self, height=None, width=None, liveCells=None):
    if width is None:
      width = self.width
    if height is None:
      height = self.height

    if liveCells is None:
      liveCells = self.liveCells

    if self.step > 0:
      self.clearGrid(height, width)

    printableGrid = [[self.deadCellChar for x in xrange(1, width)] for y in xrange(1, height)]
    for cell in liveCells:
      try:
        printableGrid[cell[1]][cell[0]] = self.liveCellChar
      except IndexError:
        # live cell is off the screen, don't worry about it.
        pass
    for row in printableGrid:
      print "".join(row)

  def outputSeed(self):
    fileName = "{}_seed.txt".format(time.time())

    finalList = []

    [finalList.append([" "]*self.width) for y in xrange(self.height)]

    for cell in self.liveCells:
      try:
        finalList[cell[1]][cell[0]] = "*"
      except IndexError:
        print "Out of bounds live cell"
        pass # Live cell is out of bounds, don't worry about it

    with open(fileName, "w") as seedFile:
      for lineList in finalList:
        seedFile.write("".join(lineList) + "\n")

life = None
def outputSeed():
  global life
  if life is not None:
    life.outputSeed()
    return False
  else:
    return True

commandDict = {
                "quit" : ("Exits the program", (lambda: True)),
                "print": ("Outputs current grid to a seed file", outputSeed),
                "continue" : ("Continue", (lambda: False))
}

def getUserInput():
  while True:
    print "What would you like to do?"
    print "Options:"
    for key, commandTup in commandDict.iteritems():
      print "  '{}' : {}".format(key, commandTup[0])
    userInput = raw_input("").strip()
    if userInput in commandDict:
      return commandDict[userInput][1]()
    else:
      print "Did not recognize command: '{}'".format(userInput)

def main():
  global life
  rows, columns = os.popen('stty size', 'r').read().split()
  life = LifeGrid(width=int(columns), height=int(rows))
  while True:
    life.printGrid()
    life.tick()
    if select.select([sys.stdin,],[],[],0.0)[0]:
      shouldBreak = getUserInput()
      if shouldBreak:
        break
    else:
      print "Press enter to pause"
      pass
    time.sleep(.1)

if __name__ == "__main__":
  main()
