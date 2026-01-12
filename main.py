import utils.variables as vs
from utils.variables import *
from  utils.sim_utils import *
from utils.sim_stats import *
from simulation.simulator import *
import traceback
from simulation.scaling_simulator import * 
import simulation.simulator_base_variabile as sbv 
from simulation.double_factor_simulation import *

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
    # if vs.MODEL == BASE:
    #     file_name = "base_model_finite_results.csv"
    #     print("FINITE BASE SIMULATION")

    if vs.TRANSIENT_ANALYSIS == 1:
        stop = STOP_ANALYSIS
        vs.REPLICATIONS = 10  # per l'analisi del transitorio facciamo meno repliche
        file_name = "base_model_transient_analysis_results.csv"
    else:
        stop = STOP
        vs.REPLICATIONS = 50  # per la simulazione normale facciamo più repliche
        file_name = "base_model_finite_results.csv"

    clear_file(file_name)
    for i in range(vs.REPLICATIONS):
        if vs.MODEL == BASE:
            print(f"start {i+1} replication")
            seed = SEED + i
            results, stats = finite_simulation(stop, seed)
            print(f"end {i+1} replication")
            write_file(results, file_name)
            append_stats(replicationStats, results, stats)
    sim_type = "base_model"

    if vs.TRANSIENT_ANALYSIS == 1:
        # analisi del transitorio
        plot_analysis(replicationStats.A_resp_interval, replicationStats.seed, "A", sim_type)
        plot_analysis(replicationStats.B_resp_interval, replicationStats.seed, "B", sim_type)
        plot_analysis(replicationStats.A1_resp_interval, replicationStats.seed, "A1", sim_type)
        plot_analysis(replicationStats.A2_resp_interval, replicationStats.seed, "A2", sim_type)
        plot_analysis(replicationStats.A3_resp_interval, replicationStats.seed, "A3", sim_type)
    else:
        
        # plot dei tempi di risposta medi per replica
        plot_replication_response_times(replicationStats.A_resp_interval, sim_type, "A")
        plot_replication_response_times(replicationStats.B_resp_interval, sim_type, "B")
        plot_replication_response_times(replicationStats.A1_resp_interval, sim_type, "A1")
        plot_replication_response_times(replicationStats.A2_resp_interval, sim_type, "A2")
        plot_replication_response_times(replicationStats.A3_resp_interval, sim_type, "A3")

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

def start_base_variabile_sim():
    """
    Avvia la simulazione con arrivi a lambda variabile,
    in modo analogo a start_simulation() per il modello base.
    """
    try:
        replicationStats = ReplicationStats()
        file_name = "base_variabile_model_finite_results.csv"
        print("FINITE BASE VARIABILE SIMULATION")

        if vs.TRANSIENT_ANALYSIS == 1:
            stop = STOP_ANALYSIS
            vs.REPLICATIONS = 10  # per l'analisi del transitorio facciamo meno repliche
        else:
            stop = STOP
            vs.REPLICATIONS = 50  # per la simulazione normale facciamo più repliche

        clear_file(file_name)

        for i in range(vs.REPLICATIONS):
            print(f"start base variabile replication {i+1}")
            seed = SEED + i
            results, stats = sbv.finite_simulation(stop, seed)  # definita in simulator_base_variabile.py

            print(f"end base variabile replication {i+1}")
            write_file(results, file_name)
            append_stats(replicationStats, results, stats)

        if vs.TRANSIENT_ANALYSIS == 1:
            # analisi del transitorio
            plot_analysis(replicationStats.A_resp_interval, replicationStats.seed, "A", "variable_lambda")
            plot_analysis(replicationStats.B_resp_interval, replicationStats.seed, "B", "variable_lambda")
            plot_analysis(replicationStats.A1_resp_interval, replicationStats.seed, "A1", "variable_lambda")
            plot_analysis(replicationStats.A2_resp_interval, replicationStats.seed, "A2", "variable_lambda")
            plot_analysis(replicationStats.A3_resp_interval, replicationStats.seed, "A3", "variable_lambda")
        else:
            sim_type = "finite_simulation"
            # plot dei tempi di risposta medi per replica
            plot_replication_response_times(replicationStats.A_resp_interval, sim_type, "A")
            plot_replication_response_times(replicationStats.B_resp_interval, sim_type, "B")
            plot_replication_response_times(replicationStats.A1_resp_interval, sim_type, "A1")
            plot_replication_response_times(replicationStats.A2_resp_interval, sim_type, "A2")
            plot_replication_response_times(replicationStats.A3_resp_interval, sim_type, "A3")

        
       
        exit(1)

    except Exception as e:
        print("Error during base variabile simulation:")
        traceback.print_exc()

def start_scaling_sim():
    """
    Avvia la simulazione con SCALING (orizzontale + spike),
    in modo analogo a start_simulation() per il modello base.
    """
    try:
        # SIMULAZIONE FINITA CON SCALING
        
        replicationStats = ReplicationStats()
        if vs.TRANSIENT_ANALYSIS == 1:
            stop = STOP_ANALYSIS
            vs.REPLICATIONS = 10  # per l'analisi del transitorio facciamo meno repliche
            file_name = "scaling_model_transient_analysis_results.csv"
        else:
            stop = STOP
            vs.REPLICATIONS = 50  # per la simulazione normale facciamo più repliche
            file_name = "scaling_model_finite_results.csv"

        print("FINITE SCALING SIMULATION")

        stop = STOP
        clear_file(file_name)

        for i in range(vs.REPLICATIONS):
            print(f"start scaling replication {i+1}")
            seed = SEED + i
            results, stats = scaling_finite_simulation(stop, seed)  # definita in scaling_simulator.py

            plot_lambda_t(stats.lambda_times, vs.SIM_TYPE, "lambda_t")
            plot_system_avg_response_time_t(stats.system_resp_times, vs.SIM_TYPE, "system_resp_t")
            plot_active_servers_t(stats.layer1_servers_times, vs.SIM_TYPE, "servers_t")

            plot_spike_active_t(stats.spike_active_times, vs.SIM_TYPE, "spike_active_t")

            print(f"end scaling replication {i+1}")
            write_file(results, file_name)
            append_stats(replicationStats, results, stats)

        sim_type = "scaling_model"

        if vs.TRANSIENT_ANALYSIS == 1:
            # analisi del transitorio
            plot_analysis(replicationStats.A_resp_interval, replicationStats.seed, "A", sim_type)
            plot_analysis(replicationStats.B_resp_interval, replicationStats.seed, "B", sim_type)
            plot_analysis(replicationStats.A1_resp_interval, replicationStats.seed, "A1", sim_type)
            plot_analysis(replicationStats.A2_resp_interval, replicationStats.seed, "A2", sim_type)
            plot_analysis(replicationStats.A3_resp_interval, replicationStats.seed, "A3", sim_type)
        else:
            
            # plot dei tempi di risposta medi per replica
            plot_replication_response_times(replicationStats.A_resp_interval, sim_type, "A")
            plot_replication_response_times(replicationStats.B_resp_interval, sim_type, "B")
            plot_replication_response_times(replicationStats.A1_resp_interval, sim_type, "A1")
            plot_replication_response_times(replicationStats.A2_resp_interval, sim_type, "A2")
            plot_replication_response_times(replicationStats.A3_resp_interval, sim_type, "A3")

       
        exit(1)

    except Exception as e:
        print("Error during scaling simulation:")
        traceback.print_exc()


def start_2fa_simulation():
    replicationStats = ReplicationStats()
    print("FINITE 2FA BASE SIMULATION")

    if vs.TRANSIENT_ANALYSIS == 1:
        stop = STOP_ANALYSIS
        vs.REPLICATIONS = 10  # per l'analisi del transitorio facciamo meno repliche
        file_name = "scaling_model_transient_analysis_results.csv"
    else:
        stop = STOP
        vs.REPLICATIONS = 50  # per la simulazione normale facciamo più repliche
        file_name = "scaling_model_finite_results.csv"

    clear_file(file_name)
    for i in range(vs.REPLICATIONS):

        print(f"start 2fa replication {i+1}")
        seed = SEED + i
        results, stats = finite_2fa_simulation(stop, seed)
        print(f"end {i+1} replication")
        write_file(results, file_name)
        append_stats(replicationStats, results, stats)

        sim_type = "2fa_model"

        if vs.TRANSIENT_ANALYSIS == 1:
            # analisi del transitorio
            plot_analysis(replicationStats.A_resp_interval, replicationStats.seed, "A", sim_type)
            plot_analysis(replicationStats.B_resp_interval, replicationStats.seed, "B", sim_type)
            plot_analysis(replicationStats.A1_resp_interval, replicationStats.seed, "A1", sim_type)
            plot_analysis(replicationStats.A2_resp_interval, replicationStats.seed, "A2", sim_type)
            plot_analysis(replicationStats.A3_resp_interval, replicationStats.seed, "A3", sim_type)
        else:
            
            # plot dei tempi di risposta medi per replica
            plot_replication_response_times(replicationStats.A_resp_interval, sim_type, "A")
            plot_replication_response_times(replicationStats.B_resp_interval, sim_type, "B")
            plot_replication_response_times(replicationStats.A1_resp_interval, sim_type, "A1")
            plot_replication_response_times(replicationStats.A2_resp_interval, sim_type, "A2")
            plot_replication_response_times(replicationStats.A3_resp_interval, sim_type, "A3")

    exit(1)


def start():
    print("1. Base model simulation")
    print("2. Base model + 2FA simulation")
    print("3. Scaling model simulation")
    print("4. Base model + variable lambda simulation")
    try:
        choice = int(input("Select the type: "))
        if choice == 1:
            get_simulation(choice)
            start_simulation()
        elif choice == 2:
            get_simulation(choice)
            start_2fa_simulation()
        elif choice == 3:
            start_scaling_sim()
        elif choice == 4:
            start_base_variabile_sim()
        else:
            print("Invalid choice.")
    except ValueError as e:
        print(f"Errore di conversione: {str(e)}")
        print(f"Tipo di errore: {type(e).__name__}")
        traceback.print_exc()  



start()
