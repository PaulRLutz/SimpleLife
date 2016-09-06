import collections

import time

import sys

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
    return [
            Cell(x=x-1, y=y-1),
            Cell(x=x,   y=y-1),
            Cell(x=x+1, y=y-1),
            Cell(x=x-1, y=y  ),
            Cell(x=x+1, y=y  ),
            Cell(x=x-1, y=y+1),
            Cell(x=x,   y=y+1),
            Cell(x=x+1, y=y+1),
           ]

  def getLiveNeighborNum(self, cell, liveCells, maxNeighbors=4):
    neighbors = self.getNeighbors(cell)
    neighborCount = 0
    for neighbor in neighbors:
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
      neighbors = self.getNeighbors(cell)
      [deadCellsToProcess.append(neighbor) for neighbor in neighbors if(neighbor not in self.liveCells and neighbor not in deadCellsToProcess)]

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

def main():
  rows, columns = os.popen('stty size', 'r').read().split()
  life = LifeGrid(width=int(columns), height=int(rows))
  while True:
    life.printGrid()
    life.tick()
    time.sleep(.1)

if __name__ == "__main__":
  main()
