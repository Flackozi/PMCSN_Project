import utils.variables as vs
from utils.variables import *
from  utils.sim_utils import *
from utils.sim_stats import *
from simulation.simulator import *

def start_simulation():
    if vs.SIM_TYPE == FINITE:
        res = start_finite_sim()
    # elif vs.SIM_TYPE == INFINITE:
    #     res = start_infinite_sim()
    else:
        print("Type not valid")
        exit(1)
    return res

def start_finite_sim():
    replicationStats = ReplicationStats()
    if vs.MODEL == BASE:
        file_name = "base_model_finite_results.csv"
        print("FINITE BASE SIMULATION")

    # if cs.TRANSIENT_ANALYSIS == 1:
    #     stop = STOP_ANALYSIS
    # else:
    stop = STOP

    for i in range(vs.REPLICATIONS):
        if vs.MODEL == BASE:
            results, stats = finite_simulation(stop)
            write_file(results, file_name)
            append_stats(replicationStats, results, stats)
            type = "replications"
            sim_type = "standard"

def start():
    print("1. Base model simulation")
    print("2. Base model + 2FA simulation")
    try:
        choice = int(input("Select the type: "))
        if choice == 1:
            get_simulation(choice)
            start_simulation()
    except ValueError:
        print("Error: invalid choice.")    


start()               