#Experiments file, it runs 10 different seeds with both pheromones on and off for each.
import os
import subprocess
import sys

#Creates results folder in project files so that csv files are stored properly and so future runs of run_experiments.py dont create an error after the first sim if the folder already exists
os.makedirs("results", exist_ok=True)

#Loop for seed and running each seed in each simulation mode: pheremones off, pheromones on
for seed in range(10):
    for mode in ["on", "off"]:
        subprocess.run([sys.executable, "sim.py", str(seed), mode], check=True) #runs the actual seeded simulations using new processes.

print("All 20 runs done. CSVs are in the results folder.")