import utils.variables as vs
from utils.variables import *
from  utils.sim_utils import *
from utils.sim_stats import *
from simulation.simulator import *
import traceback
from simulation.scaling_simulator import * 

def start_simulation():
    if vs.SIM_TYPE == FINITE:
        res = start_finite_sim()
    elif vs.SIM_TYPE == INFINITE:
        res = start_infinite_sim()
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

    clear_file(file_name)
    for i in range(vs.REPLICATIONS):
        if vs.MODEL == BASE:
            print(f"start {i+1} replication")
            results, stats = finite_simulation(stop)
            print(f"end {i+1} replication")
            write_file(results, file_name)
            append_stats(replicationStats, results, stats)
            type = "replications"
            sim_type = "standard"

def start_infinite_sim():
    # replicationStats = ReplicationStats()
    if vs.MODEL == BASE:
        file_name = "base_model_infinite_results.csv"
        print("INFINITE BASE SIMULATION")

    stop = STOP_INFINITE

    clear_file(file_name)
    batch_stats = infinite_simulation(stop)
    print("End infinite simulation")

    # type = "batch"
    # # print_simulation_stats(batch_stats, type, type)

def start_scaling_sim():
    """
    Avvia la simulazione con SCALING (orizzontale + spike),
    in modo analogo a start_simulation() per il modello base.
    Usa vs.SIM_TYPE per scegliere finita o infinita.
    """
    try:
        # SIMULAZIONE FINITA CON SCALING
        if vs.SIM_TYPE == FINITE:
            replicationStats = ReplicationStats()
            file_name = "scaling_model_finite_results.csv"
            print("FINITE SCALING SIMULATION")

            stop = STOP
            clear_file(file_name)

            for i in range(vs.REPLICATIONS):
                print(f"start scaling replication {i+1}")
                results, stats = scaling_finite_simulation(stop)  # definita in scaling_simulator.py
                print(f"end scaling replication {i+1}")
                write_file(results, file_name)
                append_stats(replicationStats, results, stats)

            sim_type = "scaling_finite"  # se ti serve per eventuali print

        # SIMULAZIONE INFINITA CON SCALING
        elif vs.SIM_TYPE == INFINITE:
            file_name = "scaling_model_infinite_results.csv"
            print("INFINITE SCALING SIMULATION")

            stop = STOP_INFINITE
            clear_file(file_name)

            batch_stats = scaling_infinite_simulation(stop)  # definita in scaling_simulator.py
            print("End infinite SCALING simulation")

            # se vuoi, qui puoi fare print delle batch statistics

        else:
            print("Type not valid (SIM_TYPE)")
            exit(1)

    except Exception as e:
        print("Error during scaling simulation:")
        traceback.print_exc()


def start():
    print("1. Base model simulation")
    print("2. Base model + 2FA simulation")
    print("3. Scaling model simulation")
    try:
        choice = int(input("Select the type: "))
        if choice == 1:
            get_simulation(choice)
            start_simulation()
        elif choice == 2:
            get_simulation(choice)
            start_simulation()
        elif choice == 3:
            get_simulation(choice)
            start_scaling_sim()
        else:
            print("Invalid choice.")
    except ValueError as e:
        print(f"Errore di conversione: {str(e)}")
        print(f"Tipo di errore: {type(e).__name__}")
        traceback.print_exc()  



start()
