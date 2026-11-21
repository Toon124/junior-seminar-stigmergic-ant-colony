# Measuring Artificial Stigmergic Adaptation using a Simulated Ant Colony

Junior Seminar, Justin Piggs, Group E

This project is a simulated ant colony in Python. Ants search for food, carry it back to their nest, and deposit pheromone trails that other ants can follow. Ants do not have direct communication with one another and only have the indirect communication of pheromone trails, this is known as stigmergy. The project aims to answer can stigmergy be displayed in a simulated colony, and does it improve foraging? It also asks how quick the ants can adapt to changes in their environment, such as changing the location of food.

## Simulation

The simulation consists of the world, the ant colony, nest, and food. Feel free to change all of the settings of the world and experiment with different pheromone strengths, evaporation rates, colony sizes, nest locations etc.

### The World
The world is a 20x20 grid with the nest at the cell (2,2), there is a wall on row 10 to break the pathway of the ants and show pheromone influence. There are 3 piles of food that each have 200 bites of food. This is achieved through the use of 3 grids all 20x20 1 holding pheromone content, 1  holding the grids occupancy (number of ants in a cell, default number allowed is 1, can be changed with CAPACITY), and if the cell contains a wall. Each tick of the simulation all of the pheromone in each cell evaporates a little simulating real pheromone trails and allowing stronger pheromones on active trails.

### The Ant Colony
The ant colony consists of 50 ants. Only 1 ant can occupy a cell at a time except at the nest. Ants are either searching the grid for food or carrying food back to the nest, searching ants follow pheromone trails 90% of the time and carrying ants head home 90% of the time. All ants wander randomly the other 10% of the time to lead to a little exploration and allow for discovery of other food sources. Ants that are carrying food decrease their pheromone strength the closer they get to the nest to promote stronger trails near the food.

### The Nest
The Nest is a tuple where the ants are created and make trips back and forth to searching for and carrying food back to the nest. It is unaffected by occupancy as all ants start and return there. Like real ants all the ants have a sort of vector that allows them to know where the nest is in relation to them, allowing them to return and deposit pheromone from a food source back to the nest.

### The Food
The food is represented by 3 dictionaries that have an x coordinate, a y coordinate, and an amount of bites left in the pile.

## Setup

```
git clone https://github.com/Toon124/junior-seminar-stigmergic-ant-colony.git
cd junior-seminar-stigmergic-ant-colony
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Running

```
python sim.py
python sim.py 3 off
python run_experiments.py
python plots.py
```

- `python sim.py` runs one simulation and prints the grid.
- `python sim.py 3 off` runs a specific seed and mode. Pick any seed number and `on` or `off` for pheromones. This saves the run as a CSV in `results/` instead of printing the grid.
- `python run_experiments.py` runs seeds 0-9 with pheromones on and off.
- `python plots.py` makes the charts from those runs.