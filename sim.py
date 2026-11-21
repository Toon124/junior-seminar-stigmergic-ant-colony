#Ant colony simulation: ants search for food, carry it home, and leave pheromone trails that other ants follow. It measures stigmergic adaptation as the ants do not directcly communicate
#Run "python sim.py" to watch one run, or "python sim.py SEED on/off" for a single experiment run.
import random
import numpy as np
import csv
import sys
import os

#World & colony settings (feel free to change!)
SEED = 0
GRID_SIZE = 20
ANT_NUM = 50
CELL_CAPACITY = 1
TICKS = 1000
NEST = (2,2)
LOG_FILE = "run_log.csv"
SHOW_GRID = True

#Settings for pheromones
PHEROMONES_ON = True
DEPOSIT = 1.0   #An ant's deposit of pheromone
TRAIL_DECAY = 0.95  #Decay away from food so that the bias towards the food actually simulates real ant pheromones (prevents trail strength from being the same at all points)
EVAPORATION = 0.99  #Slow evaporation of pheromones to increase pull towards active trails
EXPLORE = 0.1   #Ants venture off trials 10% of the time if not carrying food which allows finding new food
BASE_WEIGHT = 0.05  #Base weight of grid cells

#Food changing settings
FOOD_AMOUNT = 200
RELOCATE_TICK = 500
NEW_FOOD_SPOTS = [(17, 17), (17, 2), (6, 15)]

#Directions are respectively up, dpwn, left, and right
DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)] 

#If a seed and mode (on/off) are typed after sim.py that simulation will run without printing the grid and only save the CSV.
if len(sys.argv) == 3:
    SEED = int(sys.argv[1])
    PHEROMONES_ON = sys.argv[2] == "on"
    SHOW_GRID = False
    LOG_FILE = f"results/seed{SEED}_{sys.argv[2]}.csv"
    os.makedirs("results", exist_ok=True)


random.seed(SEED)

#Setting up simulated world (The world is three different grids that determine pheromone content of a cell, how occupied a cell is, and if a wall is in that cell or not)
pheromone = np.zeros((GRID_SIZE,GRID_SIZE))
occupancy = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
walls = np.zeros((GRID_SIZE, GRID_SIZE), dtype=bool)

#Adding a wall from columns 8-12 on row 10(Feel free to add walls wherever you like)
for x in range(8, 13):
    walls[10][x] = True

#Food locations
food = [
    {"x":16, "y":7, "amount": FOOD_AMOUNT},
    {"x":4, "y":19, "amount": FOOD_AMOUNT},
    {"x":9, "y":9, "amount": FOOD_AMOUNT},
]

deliveries = 0


#Checks coordinates to see if food is located there
def check_food(x, y):
    for pile in food:
        if pile["x"] == x and pile["y"] == y and pile["amount"] > 0:
            return True
    return False

#Takes one bite of food from the pile located at the x and y coordinates
def take_food(x, y):
    for pile in food:
        if pile["x"] == x and pile["y"] == y:
            pile["amount"] -= 1
            return

#Checks if the ant can enter certain coordinates on the grid
def can_enter(x, y):
    if x < 0 or x >= GRID_SIZE or y < 0 or y >= GRID_SIZE:
        return False
    if walls[y][x]:
        return False
    if (x, y) != NEST and occupancy[y][x] >= CELL_CAPACITY:
        return False
    return True

#Prints the world out in the terminal
def print_grid():
    for y in range(GRID_SIZE):
        row = ""
        for x in range(GRID_SIZE):
            if walls[y][x]:
                row += "#"
            elif (x, y) == NEST:
                row += "N"
            elif occupancy[y][x] > 0:
                row += "A"
            elif check_food(x, y):
                row += "F"
            elif pheromone[y][x] > 0.1:
                row += "*"
            else:
                row += "."
        print(row)



class Ant:
    #Creates ant at base state; not carrying anything and not depositing pheromones
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.carrying = False
        self.scent = 0 

    #If an ant can enter a cell it allows it to move into that cell and updates the occupancy grid
    def try_step(self, dx, dy):
        nx = self.x + dx
        ny = self.y + dy
        if not can_enter(nx, ny):
            return False

        occupancy[self.y][self.x] -= 1
        self.x = nx
        self.y = ny
        occupancy[self.y][self.x] += 1
        return True

    #Gives the ant a memory of home and allows it to return to the nest coordinates
    def home_directions(self):
        here = abs(self.x - NEST[0]) + abs(self.y - NEST[1])
        options = []
        for dx, dy in DIRECTIONS:
            there = abs(self.x + dx - NEST[0]) + abs(self.y + dy - NEST[1])
            if there < here:
                options.append((dx, dy))
        return options

    #Moves the ant based on its state, if it is carrying it moves towards the nest 90% of the time, if it is searching for food it follows pheromones 90% of the time. All ants move randomly 10% of the time
    def move(self):
        if self.carrying:
            options = self.home_directions()
            if options and random.random() < 0.9:
                dx, dy = random.choice(options)
            else:
                dx, dy = random.choice(DIRECTIONS)

        elif PHEROMONES_ON and random.random() >= EXPLORE:
            dx, dy = self.scent_direction()
        else:
            dx, dy = random.choice(DIRECTIONS)
        self.try_step(dx, dy)

    #Uses surrounding cells' pheromone content to decide where to move. The choice is weighted by the pheromone content, not directly chosen
    def scent_direction(self):
        weights = []
        for dx, dy in DIRECTIONS:
            nx = self.x + dx
            ny = self.y + dy
            if can_enter(nx, ny):
                weights.append(pheromone[ny][nx] + BASE_WEIGHT)
            else:
                weights.append(0)
        if sum(weights) == 0:
            return random.choice(DIRECTIONS)
        return random.choices(DIRECTIONS, weights=weights)[0]

#Nest doesn't have a cell capcacity, because the entire colony starts and returns there.
ants = []
for i in range(ANT_NUM):
    ant = Ant(*NEST)
    ants.append(ant)
    occupancy[NEST[1]][NEST[0]] += 1

if SHOW_GRID:
    print("Tick 0")
    print_grid()

#Main Loop: Writes each row of a CSV as it runs each tick of the simulation
with open(LOG_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["tick", "deliveries", "carrying", "food_left"])

    for tick in range(1, TICKS + 1):
        #Moves the food to the new locations in the middle of the run
        if tick == RELOCATE_TICK:
            for i in range(len(food)):
                food[i]["x"] = NEW_FOOD_SPOTS[i][0]
                food[i]["y"] = NEW_FOOD_SPOTS[i][1]
            if SHOW_GRID:
                print(f"Tick {tick}: food moved")
                print_grid()

        for ant in ants:
            ant.move()

            #When ants aren't carrying food and find it they pick it up and begin leaving pheromone 
            if not ant.carrying and check_food(ant.x, ant.y):
                take_food(ant.x, ant.y)
                ant.carrying = True
                ant.scent = DEPOSIT

            #Ants drop off food and deliveries increases by one when they reach the nest
            elif ant.carrying and (ant.x, ant.y) == NEST:
                ant.carrying = False
                deliveries += 1

            #Causes trail decay so pheromones are stronger the closer you get to food sources
            if PHEROMONES_ON and ant.carrying:
                pheromone[ant.y][ant.x] += ant.scent
                ant.scent *= TRAIL_DECAY

        #Checks to ensure that each ant is only counted once
        assert occupancy.sum() == ANT_NUM, f"Ant count wrong at tick {tick}"

        #Trails evaporate a little each tick
        if PHEROMONES_ON:
            pheromone *= EVAPORATION

        carrying = 0
        for ant in ants:
            if ant.carrying:
                carrying += 1

        food_left = 0
        for pile in food:
            food_left += pile["amount"]

        writer.writerow([tick, deliveries, carrying, food_left])
        
        #Prints the grid every 100 ticks so you can watch the trails form
        if SHOW_GRID and tick % 100 == 0 and tick != RELOCATE_TICK and tick != TICKS:
            print(f"Tick {tick}: {deliveries} deliveries")
            print_grid()

if SHOW_GRID:
    print(f"Tick {TICKS}")
    print_grid()

print(f"Seed {SEED}, pheromones {'on' if PHEROMONES_ON else 'off'}: {deliveries} deliveries")
for pile in food:
    print(pile)