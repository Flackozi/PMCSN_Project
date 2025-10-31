from utils.sim_utils import*
from utils.sim_output import *
from libraries.rngs import *
from utils.sim_stats import*
from utils.variables import *

plantSeeds(SEED)

time_checkpoints = list(range(0, STOP_ANALYSIS, 1000))  # Checkpoint each 1000 sec
current_checkpoint = 0

def finite_simulation(stop):
    global current_checkpoint
    current_checkpoint = 0
    s = getSeed()
    reset_arrival_temp()

    stats = SimulationStats()
    stats.reset(vs.START)

    # schedule first external arrival
    stats.t.arrival = GetArrival()

    while (stats.t.arrival < stop_time) or (len(stats.A_jobs) + len(stats.B_jobs) + stats.number_P > 0):
        execute(stats, stop_time)
        

    stats.calculate_area_queue()
    # horizon = stats.t.current (last time)
    return return_stats(stats, stats.t.current), stats