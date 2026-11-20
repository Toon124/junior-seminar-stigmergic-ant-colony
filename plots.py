import csv
import os
import numpy as np
import matplotlib.pyplot as plt

#Plot Settings
SEEDS = range(10)
RELOCATE_TICK = 500
WINDOW = 100
RECOVERY = 0.5
COLORS = {"on": "#2a78d6", "off": "#eb6834"}
LABELS = {"on": "Pheromones ON", "off": "Pheromones OFF"}

#Reads in a run's CSV and returns its deliveries as a list
def load_deliveries(seed, mode):
    deliveries = []
    with open(f"results/seed{seed}_{mode}.csv") as f:
        for row in csv.DictReader(f):
            deliveries.append(int(row["deliveries"]))
    return deliveries

#Takes in deliveries and returns the number of ticks it takes for ants to recover to a consistent(half their previous)delivery rate
def response_time(deliveries):
    before_move = deliveries[RELOCATE_TICK - 1] - deliveries[RELOCATE_TICK - 1 - WINDOW]
    for t in range(RELOCATE_TICK + WINDOW, len(deliveries) + 1):
        rate = deliveries[t-1] - deliveries[t - 1 - WINDOW]
        if rate >= RECOVERY * before_move:
            return t - RELOCATE_TICK
    return None

#Creates plots directory if it doesn't exist and prevents its creation and therefore an error if it does
os.makedirs("plots", exist_ok=True)

#Loads the data in from each of the CSV files into their resoective table depending on if its an off or an on run
data = {}
for mode in ["on", "off"]:
    runs = []
    for seed in SEEDS:
        runs.append(load_deliveries(seed, mode))
    data[mode]= np.array(runs)

ticks = np.arange(1, data["on"].shape[1]+ 1)

#Averages the final delivery rate for each of the mode's across each run and provides a comparison.
on_avg = data["on"][:, -1].mean()
off_avg = data["off"][:, -1].mean()
print("Pheromones ON average:", on_avg)
print("Pheromones OFF average:", off_avg)
print("Pheromones deliver", round(on_avg / off_avg, 1), "times more food")

#Gets the response time for each pheromone run and averages the times.
times = []
for run in data["on"]:
    times.append(response_time(run))
print("Response time per seed:", times)
print("Average response time:", np.mean(times), "ticks")

#Chart 1: Total deliveries over time
for mode in ["on", "off"]:
    plt.plot(ticks, data[mode].mean(axis=0), color=COLORS[mode], label=LABELS[mode])
plt.axvline(RELOCATE_TICK, color="gray", linestyle="--", label="Food moved")
plt.title("Total deliveries over time (average of 10 seeds)")
plt.xlabel("Tick")
plt.ylabel("Deliveries")
plt.legend()
plt.savefig("plots/deliveries_over_time.png", dpi=200)
plt.close()

#Chart 2: Delivery rate
for mode in ["on", "off"]:
    rate = data[mode][:, WINDOW:] - data[mode][:, :-WINDOW]
    plt.plot(ticks[WINDOW:], rate.mean(axis=0), color=COLORS[mode], label=LABELS[mode])
plt.axvline(RELOCATE_TICK, color="gray", linestyle="--", label="Food moved")
plt.title(f"Deliveries per {WINDOW} ticks (average of 10 seeds)")
plt.xlabel("Tick")
plt.ylabel(f"Deliveries in last {WINDOW} ticks")
plt.legend()
plt.savefig("plots/delivery_rate.png", dpi=200)
plt.close()

#Chart 3: Final totals
plt.bar([LABELS["on"], LABELS["off"]], [on_avg, off_avg], color=[COLORS["on"], COLORS["off"]])
plt.title("Total deliveries after 1000 ticks (average of 10 seeds)")
plt.ylabel("Deliveries")
plt.savefig("plots/total_deliveries.png", dpi=200)
plt.close()

print("Charts saved in the plots folder.")