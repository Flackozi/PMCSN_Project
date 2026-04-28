import utils.variables as vs
from utils.variables import *
from  utils.sim_utils import *
from utils.sim_stats import *
from simulation.simulator import *
import traceback
from simulation.scaling_simulator import * 
import simulation.simulator_base_variabile as sbv 
from simulation.double_factor_simulation import *
from simulation.hyperexponential_simulator import *
import simulation.realistic_simulator as rs
from simulation.double_factor_variabile_simulator import finite_2fa_variabile_simulation

def start_base_simulation():
    if vs.SIM_TYPE == FINITE:
        start_finite_simulation()
    elif vs.SIM_TYPE == INFINITE:
        start_infinite_simulation()
    else:
        print("Type not valid")
        exit(1)


def start_2fa_simulation():
    if vs.SIM_TYPE == FINITE:
        start_2fa_finite_simulation()
    elif vs.SIM_TYPE == INFINITE:
        start_2fa_infinite_simulation()
    else:
        print("Type not valid")
        exit(1)


def start_finite_simulation():
    replicationStats = ReplicationStats()
    

    if vs.TRANSIENT_ANALYSIS == 1:
        stop = STOP_ANALYSIS
        vs.REPLICATIONS = 10  # per l'analisi del transitorio facciamo meno repliche
        file_name = "base_model_transient_analysis_results.csv"
        print("TRANSIENT BASE SIMULATION")
    else:
        stop = STOP
        vs.REPLICATIONS = 50  # per la simulazione normale facciamo più repliche
        file_name = "base_model_finite_results.csv"
        print("FINITE BASE SIMULATION")

    clear_file(file_name)
    for i in range(vs.REPLICATIONS):
        if vs.MODEL == BASE:
            print(f"start {i+1} replication")
            results, stats = finite_simulation(stop)
            print(f"end {i+1} replication")
            write_file(results, file_name)
            append_stats(replicationStats, results, stats)

    sim_type = "base_model"

    if vs.TRANSIENT_ANALYSIS == 1:
        # analisi del transitorio
        plot_analysis(replicationStats.A_resp_interval, replicationStats.seed, "A", sim_type)
        plot_analysis(replicationStats.B_resp_interval, replicationStats.seed, "B", sim_type)
        plot_analysis(replicationStats.P_resp_interval, replicationStats.seed, "P", sim_type)
        plot_analysis(replicationStats.A1_resp_interval, replicationStats.seed, "A1", sim_type)
        plot_analysis(replicationStats.A2_resp_interval, replicationStats.seed, "A2", sim_type)
        plot_analysis(replicationStats.A3_resp_interval, replicationStats.seed, "A3", sim_type)
        
    else:
        
        # plot dei tempi di risposta medi per replica
        plot_replication_response_times(replicationStats.A_resp_interval, sim_type, "A")
        plot_replication_response_times(replicationStats.B_resp_interval, sim_type, "B")
        plot_replication_response_times(replicationStats.P_resp_interval, sim_type, "P")
        plot_replication_response_times(replicationStats.A1_resp_interval, sim_type, "A1")
        plot_replication_response_times(replicationStats.A2_resp_interval, sim_type, "A2")
        plot_replication_response_times(replicationStats.A3_resp_interval, sim_type, "A3")

        sim_type = "finite_simulation/base_model"
        plot_num_jobs_t(stats.Nsys_times, sim_type, f"Nsys", ylabel="N system")
        plot_num_jobs_t(stats.NA_times,   sim_type, f"NA",   ylabel="N A")
        plot_num_jobs_t(stats.NB_times,   sim_type, f"NB",   ylabel="N B")
        plot_num_jobs_t(stats.NP_times,   sim_type, f"NP",   ylabel="N P")

        

def start_infinite_simulation():
    
    if vs.MODEL == BASE:
        file_name = "base_model_infinite_results.csv"
        print("INFINITE BASE SIMULATION")

    stop = STOP_INFINITE

    clear_file(file_name)
    rep_stats, batch_stats, stats = infinite_simulation(stop)
    print("End infinite simulation")

    #salvo tutte le statistiche della replica in un file

    for res in rep_stats:
        write_file(res, "base_model_infinite_results.csv")

    remove_batch(batch_stats, 5)  # 5 batch × 3400 s = 17000 s ≈ 8.7 τ_mix (τ_mix ≈ 1961 s)

    if PRINT_PLOT_BATCH == 1:
        sim_type = "base_model"
        plot_batch(batch_stats.system_avg_response_time, sim_type, "system")
        plot_batch(batch_stats.A_avg_resp, sim_type, "center_A")
        plot_batch(batch_stats.B_avg_resp, sim_type, "center_B")
        plot_batch(batch_stats.P_avg_resp, sim_type, "center_P")
        plot_batch(batch_stats.A1_avg_resp, sim_type, "class_1_A")
        plot_batch(batch_stats.A2_avg_resp, sim_type, "class_2_A")
        plot_batch(batch_stats.A3_avg_resp, sim_type, "class_3_A")
        
        sim_type = "infinite_simulation/base_model"
        plot_num_jobs_t(batch_stats.A_avg_num_job, sim_type, "num_jobs_A", ylabel="Average number of jobs in A")
        plot_num_jobs_t(batch_stats.B_avg_num_job, sim_type, "num_jobs_B", ylabel="Average number of jobs in B")
        plot_num_jobs_t(batch_stats.P_avg_num_job, sim_type, "num_jobs_P", ylabel="Average number of jobs in P")
        plot_num_jobs_t(batch_stats.system_avg_num_job, sim_type, "num_jobs_system", ylabel="Average number of jobs in system")

    print_simulation_stats(batch_stats, "replications")


def start_base_variabile_sim():
    """
    Avvia la simulazione con arrivi a lambda variabile,
    in modo analogo a start_simulation() per il modello base.
    """
    try:
        replicationStats = ReplicationStats()
        
        print("FINITE BASE VARIABILE LAMBDA SIMULATION")

        if vs.TRANSIENT_ANALYSIS == 1:
            file_name = "base_variabile_lambda_model_transient_analysis_results.csv"
            stop = STOP_ANALYSIS
            vs.REPLICATIONS = 10  # per l'analisi del transitorio facciamo meno repliche
        else:
            file_name = "base_variabile_lambda_model_finite_results.csv"
            stop = STOP
            vs.REPLICATIONS = 50  # per la simulazione normale facciamo più repliche

        clear_file(file_name)

        for i in range(vs.REPLICATIONS):
            print(f"start base variabile lambda replication {i+1}")
            results, stats = sbv.finite_simulation(stop)  # definita in simulator_base_variabile.py

            print(f"end base variabile lambda replication {i+1}")
            write_file(results, file_name)
            append_stats(replicationStats, results, stats)

        sim_type = "base_variabile_lambda_model"


        if vs.TRANSIENT_ANALYSIS == 1:
            # analisi del transitorio
            plot_analysis(replicationStats.A_resp_interval, replicationStats.seed, "A", sim_type)
            plot_analysis(replicationStats.B_resp_interval, replicationStats.seed, "B", sim_type)
            plot_analysis(replicationStats.P_resp_interval, replicationStats.seed, "P", sim_type)
            plot_analysis(replicationStats.A1_resp_interval, replicationStats.seed, "A1", sim_type)
            plot_analysis(replicationStats.A2_resp_interval, replicationStats.seed, "A2", sim_type)
            plot_analysis(replicationStats.A3_resp_interval, replicationStats.seed, "A3", sim_type)
        else:
            # plot dei tempi di risposta medi per replica
            plot_replication_response_times(replicationStats.A_resp_interval, sim_type, "A")
            plot_replication_response_times(replicationStats.B_resp_interval, sim_type, "B")
            plot_replication_response_times(replicationStats.P_resp_interval, sim_type, "P")
            plot_replication_response_times(replicationStats.A1_resp_interval, sim_type, "A1")
            plot_replication_response_times(replicationStats.A2_resp_interval, sim_type, "A2")
            plot_replication_response_times(replicationStats.A3_resp_interval, sim_type, "A3")

        
       
        exit(1)

    except Exception as e:
        print("Error during base variabile lambda simulation:")
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
            sim_type = "transient_analysis/scaling_model"

        else:
            stop = STOP
            vs.REPLICATIONS = 1  # per la simulazione normale facciamo più repliche
            file_name = "scaling_model_finite_results.csv"
            sim_type = "finite_simulation/scaling_model"


        print("FINITE SCALING SIMULATION")

        
        clear_file(file_name)

        for i in range(vs.REPLICATIONS):
            print(f"start scaling replication {i+1}")
            results, stats = scaling_finite_simulation(stop)  # definita in scaling_simulator.py

            print(f"end scaling replication {i+1}")
            write_file(results, file_name)
            append_stats(replicationStats, results, stats)

        plot_lambda_t(stats.lambda_times, sim_type, "lambda_t")
        plot_system_avg_response_time_t(stats.system_resp_times, sim_type, "system_resp_t")
        plot_active_servers_t(stats.layer0_servers_times, sim_type, "servers_A_t", ylabel="Active servers (A)")
        plot_active_servers_t(stats.layer1_servers_times, sim_type, "servers_B_t", ylabel="Active servers (B)")
        plot_spike_active_t(stats.spike_active_times, sim_type, "spike_B_active_t", ylabel="Spike B active (0/1)")
        plot_spike_active_t(stats.spike_A_active_times, sim_type, "spike_A_active_t", ylabel="Spike A active (0/1)")

        sim_type = "scaling_model"

        if vs.TRANSIENT_ANALYSIS == 1:
            # analisi del transitorio
            plot_analysis(replicationStats.A_resp_interval, replicationStats.seed, "A", sim_type)
            plot_analysis(replicationStats.B_resp_interval, replicationStats.seed, "B", sim_type)
            plot_analysis(replicationStats.P_resp_interval, replicationStats.seed, "P", sim_type)
            plot_analysis(replicationStats.A1_resp_interval, replicationStats.seed, "A1", sim_type)
            plot_analysis(replicationStats.A2_resp_interval, replicationStats.seed, "A2", sim_type)
            plot_analysis(replicationStats.A3_resp_interval, replicationStats.seed, "A3", sim_type)
        else:
            
            # plot dei tempi di risposta medi per replica
            plot_replication_response_times(replicationStats.A_resp_interval, sim_type, "A")
            plot_replication_response_times(replicationStats.B_resp_interval, sim_type, "B")
            plot_replication_response_times(replicationStats.P_resp_interval, sim_type, "P")
            plot_replication_response_times(replicationStats.A1_resp_interval, sim_type, "A1")
            plot_replication_response_times(replicationStats.A2_resp_interval, sim_type, "A2")
            plot_replication_response_times(replicationStats.A3_resp_interval, sim_type, "A3")

       
        exit(1)

    except Exception as e:
        print("Error during scaling simulation:")
        traceback.print_exc()


def start_2fa_finite_simulation():
    replicationStats = ReplicationStats()
    print("FINITE 2FA BASE SIMULATION")

    if vs.TRANSIENT_ANALYSIS == 1:
        stop = STOP_ANALYSIS
        vs.REPLICATIONS = 10  # per l'analisi del transitorio facciamo meno repliche
        file_name = "2fa_model_transient_analysis_results.csv"
    else:
        stop = STOP
        vs.REPLICATIONS = 50  # per la simulazione normale facciamo più repliche
        file_name = "2fa_model_finite_results.csv"
    clear_file(file_name)
    for i in range(vs.REPLICATIONS):

        print(f"start 2fa replication {i+1}")
        results, stats = finite_2fa_simulation(stop)
        print(f"end {i+1} replication")
        write_file(results, file_name)
        append_stats(replicationStats, results, stats)

    sim_type = "2fa_model"

    if vs.TRANSIENT_ANALYSIS == 1:
        # analisi del transitorio
        plot_analysis(replicationStats.A_resp_interval, replicationStats.seed, "A", sim_type)
        plot_analysis(replicationStats.B_resp_interval, replicationStats.seed, "B", sim_type)
        plot_analysis(replicationStats.P_resp_interval, replicationStats.seed, "P", sim_type)
        plot_analysis(replicationStats.A1_resp_interval, replicationStats.seed, "A1", sim_type)
        plot_analysis(replicationStats.A2_resp_interval, replicationStats.seed, "A2", sim_type)
        plot_analysis(replicationStats.A3_resp_interval, replicationStats.seed, "A3", sim_type)
    else:
        
        # plot dei tempi di risposta medi per replica
        plot_replication_response_times(replicationStats.A_resp_interval, sim_type, "A")
        plot_replication_response_times(replicationStats.B_resp_interval, sim_type, "B")
        plot_replication_response_times(replicationStats.P_resp_interval, sim_type, "P")
        plot_replication_response_times(replicationStats.A1_resp_interval, sim_type, "A1")
        plot_replication_response_times(replicationStats.A2_resp_interval, sim_type, "A2")
        plot_replication_response_times(replicationStats.A3_resp_interval, sim_type, "A3")


    exit(1)


def start_2fa_infinite_simulation():
    if vs.MODEL == BASE:
        file_name = "2fa_model_infinite_results.csv"
        print("INFINITE 2FA SIMULATION")

    clear_file(file_name)
    rep_stats, batch_stats, stats = infinite_2fa_simulation(STOP_INFINITE)
    print("End infinite 2fa simulation")

    for res in rep_stats:
        write_file(res, "2fa_model_infinite_results.csv")
    
    remove_batch(batch_stats, 5)  # 5 batch × 3400 s = 17000 s ≈ 8.7 τ_mix (τ_mix ≈ 1961 s)
    
    if PRINT_PLOT_BATCH == 1:
        sim_type = "2fa_model"
        plot_batch(batch_stats.system_avg_response_time, sim_type, "system")
        plot_batch(batch_stats.A_avg_resp, sim_type, "center_A")
        plot_batch(batch_stats.B_avg_resp, sim_type, "center_B")
        plot_batch(batch_stats.P_avg_resp, sim_type, "center_P")
        plot_batch(batch_stats.A1_avg_resp, sim_type, "class_1_A")
        plot_batch(batch_stats.A2_avg_resp, sim_type, "class_2_A")
        plot_batch(batch_stats.A3_avg_resp, sim_type, "class_3_A")

        sim_type = "infinite_simulation/2fa_model"
        plot_num_jobs_t(batch_stats.A_avg_num_job, sim_type, "num_jobs_A", ylabel="Average number of jobs in A")
        plot_num_jobs_t(batch_stats.B_avg_num_job, sim_type, "num_jobs_B", ylabel="Average number of jobs in B")
        plot_num_jobs_t(batch_stats.P_avg_num_job, sim_type, "num_jobs_P", ylabel="Average number of jobs in P")
        plot_num_jobs_t(batch_stats.system_avg_num_job, sim_type, "num_jobs_system", ylabel="Average number of jobs in system")
        print_simulation_stats(batch_stats, "replications")

    

def start_hyperexponential_simulation():
    if vs.SIM_TYPE == INFINITE:
        file_name = "hyper_model_infinite_results.csv"
        print("INFINITE HYPEREXPONENTIAL SIMULATION")

        clear_file(file_name)
        hyper_infinite_simulation(STOP_INFINITE)
        print("End infinite hyperexponential simulation")
    else:
        replicationStats = ReplicationStats()
        print("FINITE HYPEREXPONENTIAL BASE SIMULATION")
        
        if vs.TRANSIENT_ANALYSIS == 1:
            stop = STOP_ANALYSIS
            vs.REPLICATIONS = 10  # per l'analisi del transitorio facciamo meno repliche
            file_name = "hyperexponential_model_transient_analysis_results.csv"
        else:
            stop = STOP
            vs.REPLICATIONS = 50  # per la simulazione normale facciamo più repliche
            file_name = "hyperexponential_model_finite_results.csv"

        clear_file(file_name)
        for i in range(vs.REPLICATIONS):
            if vs.MODEL == BASE:
                print(f"start {i+1} replication")
                results, stats = hyper_finite_simulation(stop)
                print(f"end {i+1} replication")
                write_file(results, file_name)
                append_stats(replicationStats, results, stats)

        sim_type = "hyperexponential_model"

        if vs.TRANSIENT_ANALYSIS == 1:
            # analisi del transitorio
            plot_analysis(replicationStats.A_resp_interval, replicationStats.seed, "A", sim_type)
            plot_analysis(replicationStats.B_resp_interval, replicationStats.seed, "B", sim_type)
            plot_analysis(replicationStats.P_resp_interval, replicationStats.seed, "P", sim_type)
            plot_analysis(replicationStats.A1_resp_interval, replicationStats.seed, "A1", sim_type)
            plot_analysis(replicationStats.A2_resp_interval, replicationStats.seed, "A2", sim_type)
            plot_analysis(replicationStats.A3_resp_interval, replicationStats.seed, "A3", sim_type)
        else:
            
            # plot dei tempi di risposta medi per replica
            plot_replication_response_times(replicationStats.A_resp_interval, sim_type, "A")
            plot_replication_response_times(replicationStats.B_resp_interval, sim_type, "B")
            plot_replication_response_times(replicationStats.P_resp_interval, sim_type, "P")
            plot_replication_response_times(replicationStats.A1_resp_interval, sim_type, "A1")
            plot_replication_response_times(replicationStats.A2_resp_interval, sim_type, "A2")
            plot_replication_response_times(replicationStats.A3_resp_interval, sim_type, "A3")

            print_simulation_stats(replicationStats, "replications")


            sim_type = "finite_simulation/hyperexponential_model" 
            plot_num_jobs_t(stats.Nsys_times, sim_type, f"Nsys", ylabel="N system")
            plot_num_jobs_t(stats.NA_times,   sim_type, f"NA",   ylabel="N A")
            plot_num_jobs_t(stats.NB_times,   sim_type, f"NB",   ylabel="N B")
            plot_num_jobs_t(stats.NP_times,   sim_type, f"NP",   ylabel="N P")


def start_2fa_variabile_simulation():
    """
    Avvia la simulazione con 2FA e tasso di arrivo variabile (lambda_scaling).
    """
    try:
        replicationStats = ReplicationStats()

        print("FINITE 2FA + VARIABLE LAMBDA SIMULATION")

        if vs.TRANSIENT_ANALYSIS == 1:
            file_name = "2fa_variabile_model_transient_analysis_results.csv"
            stop = STOP_ANALYSIS
            vs.REPLICATIONS = 10
        else:
            file_name = "2fa_variabile_model_finite_results.csv"
            stop = STOP
            vs.REPLICATIONS = 50

        clear_file(file_name)

        for i in range(vs.REPLICATIONS):
            print(f"start 2fa variabile replication {i+1}")
            results, stats = finite_2fa_variabile_simulation(stop)
            print(f"end 2fa variabile replication {i+1}")
            write_file(results, file_name)
            append_stats(replicationStats, results, stats)

        sim_type = "2fa_variabile_model"

        if vs.TRANSIENT_ANALYSIS == 1:
            plot_analysis(replicationStats.A_resp_interval, replicationStats.seed, "A", sim_type)
            plot_analysis(replicationStats.B_resp_interval, replicationStats.seed, "B", sim_type)
            plot_analysis(replicationStats.P_resp_interval, replicationStats.seed, "P", sim_type)
            plot_analysis(replicationStats.A1_resp_interval, replicationStats.seed, "A1", sim_type)
            plot_analysis(replicationStats.A2_resp_interval, replicationStats.seed, "A2", sim_type)
            plot_analysis(replicationStats.A3_resp_interval, replicationStats.seed, "A3", sim_type)
        else:
            plot_replication_response_times(replicationStats.A_resp_interval, sim_type, "A")
            plot_replication_response_times(replicationStats.B_resp_interval, sim_type, "B")
            plot_replication_response_times(replicationStats.P_resp_interval, sim_type, "P")
            plot_replication_response_times(replicationStats.A1_resp_interval, sim_type, "A1")
            plot_replication_response_times(replicationStats.A2_resp_interval, sim_type, "A2")
            plot_replication_response_times(replicationStats.A3_resp_interval, sim_type, "A3")

            sim_type = "finite_simulation/2fa_variabile_model"
            plot_num_jobs_t(stats.Nsys_times, sim_type, "Nsys", ylabel="N system")
            plot_num_jobs_t(stats.NA_times,   sim_type, "NA",   ylabel="N A")
            plot_num_jobs_t(stats.NB_times,   sim_type, "NB",   ylabel="N B")
            plot_num_jobs_t(stats.NP_times,   sim_type, "NP",   ylabel="N P")

        exit(1)

    except Exception as e:
        print("Error during 2FA variable lambda simulation:")
        traceback.print_exc()


def start_realistic_simulation():
    """
    Avvia la simulazione realistica: modello base con arrivi iper-esponenziali
    e tasso di arrivo variabile (lambda_scaling).
    """
    try:
        replicationStats = ReplicationStats()

        print("FINITE REALISTIC SIMULATION (hyperexponential + variable lambda)")

        if vs.TRANSIENT_ANALYSIS == 1:
            file_name = "realistic_model_transient_analysis_results.csv"
            stop = STOP_ANALYSIS
            vs.REPLICATIONS = 10
        else:
            file_name = "realistic_model_finite_results.csv"
            stop = STOP
            vs.REPLICATIONS = 50

        clear_file(file_name)

        for i in range(vs.REPLICATIONS):
            print(f"start realistic replication {i+1}")
            results, stats = rs.realistic_finite_simulation(stop)
            print(f"end realistic replication {i+1}")
            write_file(results, file_name)
            append_stats(replicationStats, results, stats)

        sim_type = "realistic_model"

        if vs.TRANSIENT_ANALYSIS == 1:
            plot_analysis(replicationStats.A_resp_interval, replicationStats.seed, "A", sim_type)
            plot_analysis(replicationStats.B_resp_interval, replicationStats.seed, "B", sim_type)
            plot_analysis(replicationStats.P_resp_interval, replicationStats.seed, "P", sim_type)
            plot_analysis(replicationStats.A1_resp_interval, replicationStats.seed, "A1", sim_type)
            plot_analysis(replicationStats.A2_resp_interval, replicationStats.seed, "A2", sim_type)
            plot_analysis(replicationStats.A3_resp_interval, replicationStats.seed, "A3", sim_type)
        else:
            plot_replication_response_times(replicationStats.A_resp_interval, sim_type, "A")
            plot_replication_response_times(replicationStats.B_resp_interval, sim_type, "B")
            plot_replication_response_times(replicationStats.P_resp_interval, sim_type, "P")
            plot_replication_response_times(replicationStats.A1_resp_interval, sim_type, "A1")
            plot_replication_response_times(replicationStats.A2_resp_interval, sim_type, "A2")
            plot_replication_response_times(replicationStats.A3_resp_interval, sim_type, "A3")

            sim_type = "finite_simulation/realistic_model"
            plot_num_jobs_t(stats.Nsys_times, sim_type, "Nsys", ylabel="N system")
            plot_num_jobs_t(stats.NA_times,   sim_type, "NA",   ylabel="N A")
            plot_num_jobs_t(stats.NB_times,   sim_type, "NB",   ylabel="N B")
            plot_num_jobs_t(stats.NP_times,   sim_type, "NP",   ylabel="N P")

        exit(1)

    except Exception as e:
        print("Error during realistic simulation:")
        traceback.print_exc()


def start_ci_validation_comparison():
    """
    Entry point di validazione: esegue in sequenza la simulazione baseline
    e quella realistica (lambda variabile + iper-esponenziale) e produce
    un bar chart che confronta l'ampiezza dell'IC 95% dei tempi di risposta
    per i vari centri nei due scenari, oltre a tutti i plot consueti per
    entrambi gli scenari.
    """
    try:
        stop = STOP
        vs.REPLICATIONS = 50

        # --- baseline ---
        print("FINITE BASE SIMULATION (validation run)")
        base_file = "base_model_finite_results.csv"
        clear_file(base_file)
        baseReplicationStats = ReplicationStats()
        for i in range(vs.REPLICATIONS):
            print(f"start base replication {i+1}")
            results, base_stats = finite_simulation(stop)
            write_file(results, base_file)
            append_stats(baseReplicationStats, results, base_stats)

        # plot consueti baseline
        sim_type = "base_model"
        plot_replication_response_times(baseReplicationStats.A_resp_interval, sim_type, "A")
        plot_replication_response_times(baseReplicationStats.B_resp_interval, sim_type, "B")
        plot_replication_response_times(baseReplicationStats.P_resp_interval, sim_type, "P")
        plot_replication_response_times(baseReplicationStats.A1_resp_interval, sim_type, "A1")
        plot_replication_response_times(baseReplicationStats.A2_resp_interval, sim_type, "A2")
        plot_replication_response_times(baseReplicationStats.A3_resp_interval, sim_type, "A3")

        sim_type = "finite_simulation/base_model"
        plot_num_jobs_t(base_stats.Nsys_times, sim_type, "Nsys", ylabel="N system")
        plot_num_jobs_t(base_stats.NA_times,   sim_type, "NA",   ylabel="N A")
        plot_num_jobs_t(base_stats.NB_times,   sim_type, "NB",   ylabel="N B")
        plot_num_jobs_t(base_stats.NP_times,   sim_type, "NP",   ylabel="N P")

        # --- realistic ---
        print("FINITE REALISTIC SIMULATION (validation run)")
        real_file = "realistic_model_finite_results.csv"
        clear_file(real_file)
        realReplicationStats = ReplicationStats()
        for i in range(vs.REPLICATIONS):
            print(f"start realistic replication {i+1}")
            results, real_stats = rs.realistic_finite_simulation(stop)
            write_file(results, real_file)
            append_stats(realReplicationStats, results, real_stats)

        # plot consueti realistic
        sim_type = "realistic_model"
        plot_replication_response_times(realReplicationStats.A_resp_interval, sim_type, "A")
        plot_replication_response_times(realReplicationStats.B_resp_interval, sim_type, "B")
        plot_replication_response_times(realReplicationStats.P_resp_interval, sim_type, "P")
        plot_replication_response_times(realReplicationStats.A1_resp_interval, sim_type, "A1")
        plot_replication_response_times(realReplicationStats.A2_resp_interval, sim_type, "A2")
        plot_replication_response_times(realReplicationStats.A3_resp_interval, sim_type, "A3")

        sim_type = "finite_simulation/realistic_model"
        plot_num_jobs_t(real_stats.Nsys_times, sim_type, "Nsys", ylabel="N system")
        plot_num_jobs_t(real_stats.NA_times,   sim_type, "NA",   ylabel="N A")
        plot_num_jobs_t(real_stats.NB_times,   sim_type, "NB",   ylabel="N B")
        plot_num_jobs_t(real_stats.NP_times,   sim_type, "NP",   ylabel="N P")

        # --- confronto IC 95% ---
        plot_ci_width_comparison(baseline_csv=base_file,
                                 realistic_csv=real_file)

    except Exception as e:
        print("Error during CI validation comparison:")
        traceback.print_exc()


def start():

    #TODO: rimuovere simulazione iper esponenziale, 2fa e con lambda variabile
    print("1. Base model simulation")
    print("2. Base model + 2FA simulation")
    print("3. Scaling model simulation")
    print("4. Base model + variable lambda simulation")
    print("5. Base model + hyperexponential distribution")
    print("6. Realistic model (hyperexponential + variable lambda)")
    print("7. Base model + 2FA + variable lambda")
    print("8. Validation: CI width comparison baseline vs realistic")
    try:
        choice = int(input("Select the type: "))
        if choice == 1:
            get_simulation(choice)
            start_base_simulation()
        elif choice == 2:
            get_simulation(choice)
            start_2fa_simulation()
        elif choice == 3:
            start_scaling_sim()
        elif choice == 4:
            start_base_variabile_sim()
        elif choice == 5:
            get_simulation(choice)
            start_hyperexponential_simulation()
        elif choice == 6:
            start_realistic_simulation()
        elif choice == 7:
            start_2fa_variabile_simulation()
        elif choice == 8:
            get_simulation(1)
            start_ci_validation_comparison()
        else:
            print("Invalid choice.")
    except ValueError as e:
        print(f"Errore di conversione: {str(e)}")
        print(f"Tipo di errore: {type(e).__name__}")
        traceback.print_exc()



start()
