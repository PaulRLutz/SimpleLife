import collections

import time

import sys

import select

import os

Cell = collections.namedtuple("Cell", "x y")

class LifeGrid:
  SEED_LIST = "list"
  SEED_IMAGE = "image"

  def __init__(self, width=-1, height=-1, seed_file="seed.txt", seed_format=SEED_LIST, born=[3], survives=[2,3]):
    self.live_cells = self.parse_seed_file(seed_file, seed_format)
    self.step = 0

    self.born = born
    self.survives = survives

    self.maxBorn = max(self.born)+1
    self.maxSurvives = max(self.survives)+1

    self.deadCellChar = "_"
    self.liveCellChar = "O"

    self.width = width
    self.height = height

  def parse_seed_file(self, seed_file, seed_format):
    live_cells = []
    with open(seed_file, "r") as seed:
      for line_index, line in enumerate(seed):
        print("Processing line: '{}'".format(line))
        for char_index, character in enumerate(line):
          if character == "*":
            live_cells.append(Cell(x=char_index, y=line_index))
    return live_cells

  def get_neighbors(self, cell):
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

  def get_live_neighbor_num(self, cell, live_cells=None, max_neighbors=4):
    if live_cells is None:
      live_cells = self.live_cells
    neighbor_count = 0
    for neighbor in self.get_neighbors(cell):
      if neighbor in live_cells:
        neighbor_count += 1
      if neighbor_count >= max_neighbors:
        break
    return neighbor_count

  def tick(self):
    new_live_cells = []
    live_cells_to_process = list(self.live_cells)
    dead_cells_to_process = []
   
    # Populate dead_cells_to_process 
    for cell in self.live_cells:
      [dead_cells_to_process.append(neighbor) for neighbor in self.get_neighbors(cell) if(neighbor not in self.live_cells and neighbor not in dead_cells_to_process)]

    for cell in live_cells_to_process:
      if (self.width > 0 and cell[0] > self.width) or (self.height > 0 and cell[1] > self.height) or (cell[1] < 0) or (cell[0] < 0):
        continue # Don't ignore a cell if it is out of bounds (greater than width or height, or an x or y less than 0)
      if self.get_live_neighbor_num(cell, max_neighbors=self.maxSurvives) in self.survives:
        new_live_cells.append(cell)
    for cell in dead_cells_to_process:
      if (self.width > 0 and cell[0] > self.width) or (self.height > 0 and cell[1] > self.height) or (cell[1] < 0) or (cell[0] < 0):
        continue
      if self.get_live_neighbor_num(cell, max_neighbors=self.maxBorn) in self.born:
        new_live_cells.append(cell)

    self.live_cells = new_live_cells
    
    self.step += 1

  def clear_grid(self, width, height):
    os.system("clear")

  def print_grid(self, height=None, width=None, live_cells=None):
    if width is None:
      width = self.width
    if height is None:
      height = self.height

    if live_cells is None:
      live_cells = self.live_cells

    if self.step > 0:
      self.clear_grid(height, width)

    printable_grid = [[self.deadCellChar for x in range(1, width)] for y in range(1, height)]
    for cell in live_cells:
      try:
        printable_grid[cell[1]][cell[0]] = self.liveCellChar
      except IndexError:
        # live cell is off the screen, don't worry about it.
        pass
    for row in printable_grid:
      print("".join(row))

  def output_seed(self):
    file_name = "{}_seed.txt".format(time.time())

    final_list = []

    [final_list.append([" "]*self.width) for y in range(self.height)]

    for cell in self.live_cells:
      try:
        final_list[cell[1]][cell[0]] = "*"
      except IndexError:
        print("Out of bounds live cell")
        pass # Live cell is out of bounds, don't worry about it

    with open(file_name, "w") as seed_file:
      for line_list in final_list:
        seed_file.write("".join(line_list).rstrip() + "\n") # rstrip to remove unecessary trailing spaces

def output_seed(life):
  if life is not None:
    life.output_seed()
    return False
  else:
    return True

command_dict = {
                "quit" : ("Exits the program", (lambda x: True)),
                "print": ("Outputs current grid to a seed file", output_seed),
                "continue" : ("Continue", (lambda x: False))
}

def get_user_input(life):
  while True:
    print("What would you like to do?")
    print("Options:")
    for key, command_tup in command_dict.items():
      print("  '{}' : {}".format(key, command_tup[0]))
    user_input = input("").strip()
    if user_input in command_dict:
      return command_dict[user_input][1](life)
    else:
      print("Did not recognize command: '{}'".format(user_input))

def main():
  rows, columns = os.popen('stty size', 'r').read().split()
  life = LifeGrid(seed_file="common_patterns_seed.txt", width=int(columns), height=int(rows))
  while True:
    life.print_grid()
    life.tick()
    if select.select([sys.stdin,],[],[],0.0)[0]:
      should_break = get_user_input(life)
      if should_break:
        break
    else:
      print("Press enter to pause")
      pass
    time.sleep(.1)

if __name__ == "__main__":
  main()
