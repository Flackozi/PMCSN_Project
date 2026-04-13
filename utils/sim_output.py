import csv
import statistics
import matplotlib.pyplot as plt
import os
from utils.sim_utils import *
file_path = "simulation/../output/csv/"

header = ['seed', 'A_avg_resp', 'A_avg_wait', 'A_avg_serv', 'A_utilization', 'A_avg_num_job', 'A_throughput' ,'B_avg_resp',
          'B_avg_wait', 'B_avg_serv', 'B_utilization', 'B_avg_num_job', 'B_throughput', 'P_avg_resp', 'P_avg_wait', 'P_avg_serv', 
          'P_utilization', 'P_avg_num_job', 'P_throughput', 'A1_avg_resp', 'A1_avg_wait', 'A1_avg_serv', 'A2_avg_resp',
          'A2_avg_wait', 'A2_avg_serv', 'A3_avg_resp', 'A3_avg_wait', 'A3_avg_serv', 'total_completed', 'system_avg_response_time', 
          'system_avg_service_time', 'system_utilization', 'system_avg_wait', 'system_avg_num_job', 'system_throughput', 'job_arrived', 'completions_A1', 'completions_A2',
          'completions_A3', 'completions_B', 'completions_P', 'horizon']

# Funzione per scrivere i risultati della simulazione su file CSV
def write_file(results, file_name):
    file_path = "simulation/../output/csv/"
    path = file_path + file_name
    with open(path, "a", newline = '', encoding='utf-8') as csvfile:
        write = csv.DictWriter(csvfile, fieldnames=header)
        write.writerow(results)


# Funzione per creare/azzerare il file CSV con l'header
def clear_file(file_name):
    file_path = "simulation/../output/csv/"
    path = file_path + file_name
    with open(path, "w", newline = '', encoding='utf-8') as csvfile:
        write = csv.DictWriter(csvfile, fieldnames=header)
        write.writeheader()

# Funzione per plottare i tempi di attesa medi per batch in simulazioni infinite
def plot_batch(wait_times, sim_type, name):
    output_dir = f"simulation/../output/plot/infinite_simulation/{sim_type}"

    x_values = [index for index in range(len(wait_times)+1)]
    y_values = [0]
    for i in range(len(wait_times)):
        y_values.append(statistics.mean(wait_times[:i+1]))

    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, linestyle='-', color='b')
    plt.xlabel('Batch')
    plt.ylabel('Response time')
    plt.grid(True)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'{name}.png')
    plt.savefig(output_path)
    plt.close()

# Funzione per plottare lambda(t) nel tempo
def plot_lambda_t(lambda_times, sim_type, name):
    """
    lambda_times: lista di tuple (t, lambda)
    Salva in output/plot/{sim_type}/{name}.png
    """
    output_dir = f"simulation/../output/plot/{sim_type}"

    x_values = [t for t, _ in lambda_times]
    y_values = [lam for _, lam in lambda_times]

    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, linestyle='-')
    plt.xlabel('Time')
    plt.ylabel('Lambda(t)')
    plt.grid(True)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'{name}.png')
    plt.savefig(output_path)
    plt.close()

# Funzione per plottare il tempo di risposta medio del sistema nel tempo
def plot_system_avg_response_time_t(system_resp_times, sim_type, name):
    """
    system_resp_times: lista di tuple (t, Rsys_running)
    Salva in output/plot/{sim_type}/{name}.png
    """
    output_dir = f"simulation/../output/plot/{sim_type}"

    x_values = [t for t, _ in system_resp_times]
    y_values = [r for _, r in system_resp_times]

    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, linestyle='-')
    plt.xlabel('Time')
    plt.ylabel('System avg response time (running)')
    plt.grid(True)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'{name}.png')
    plt.savefig(output_path)
    plt.close()

# Funzione per plottare il numero di server attivi di layer 1 nel tempo
def plot_active_servers_t(layer1_servers_times, sim_type, name):
    """
    layer1_servers_times: lista di tuple (t, n_servers)
    Salva in output/plot/{sim_type}/{name}.png
    """
    output_dir = f"simulation/../output/plot/{sim_type}"

    x_values = [t for t, _ in layer1_servers_times]
    y_values = [n for _, n in layer1_servers_times]

    plt.figure(figsize=(10, 6))
    plt.step(x_values, y_values, where='post')
    plt.xlabel('Time')
    plt.ylabel('Active servers (Layer 1)')
    plt.grid(True)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'{name}.png')
    plt.savefig(output_path)
    plt.close()

# Funzione per plottare lo stato di attività del server spike nel tempo
def plot_spike_active_t(spike_active_times, sim_type, name):
    """
    spike_active_times: lista di tuple (t, 0/1)
    Salva in output/plot/{sim_type}/{name}.png
    """
    output_dir = f"simulation/../output/plot/{sim_type}"

    if not spike_active_times:
        spike_active_times = [(0, 0)]

    x_values = [t for t, _ in spike_active_times]
    y_values = [a for _, a in spike_active_times]

    plt.figure(figsize=(10, 6))
    plt.step(x_values, y_values, where='post')
    plt.xlabel('Time')
    plt.ylabel('Spike server active (0/1)')
    plt.ylim(-0.1, 1.1)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'{name}.png')
    plt.savefig(output_path)
    plt.close()

# Funzione che plotta i tempi di risposta in funzione del tempo (una serie per ogni replica)
def plot_replication_response_times(resp_times, sim_type, name):
    output_dir = f"simulation/../output/plot/finite_simulation/{sim_type}"

    # resp_times è una lista di repliche, ogni replica è una lista di tuple (time, avg_resp_time)
    plt.figure(figsize=(10, 6))
    
    # Plotta la serie temporale di ogni replica
    for replica_index, replica_series in enumerate(resp_times):
        if replica_series:
            times = [point[0] for point in replica_series]
            resp_values = [point[1] for point in replica_series]
            plt.plot(times, resp_values, alpha=0.7)
    
    plt.xlabel('Time (s)')
    plt.ylabel('Response time (s)')
    plt.grid(True)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'{name}.png')
    plt.savefig(output_path)
    plt.close()

# Funzone per il plot dell'analisi del transitorio
def plot_analysis(resp_times, seed, name, sim_type):
    output_dir = f"simulation/../output/plot/transient_analysis/{sim_type}"

    plt.figure(figsize=(10, 6))

    for run_index, response_times in enumerate(resp_times):
        times = [point[0] for point in response_times]
        avg_response_times = [point[1] for point in response_times]
        plt.plot(times, avg_response_times, label=f'Seed {seed[run_index]}')

    plt.xlabel('Time (s)')
    plt.ylabel('Resp time (s)')
    plt.legend()
    plt.grid(True)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'{name}.png')
    plt.savefig(output_path)
    plt.close()


# serve a fare il plot della popolazione di jobs nel sistema nel tempo. Usato principalmente per confronto tra Exponential e HyperExponential
def plot_num_jobs_t(num_jobs_times, sim_type, name, ylabel="Number of jobs"):
    """
    num_jobs_times: lista di tuple (t, N) per time series, o lista di float per batch means
    Salva in output/plot/{sim_type}/{name}.png
    """
    output_dir = f"simulation/../output/plot/{sim_type}"

    if not num_jobs_times:
        return

    # Determina se è una serie temporale o medie per batch
    if isinstance(num_jobs_times[0], tuple):
        # Time series
        x_values = [t for t, _ in num_jobs_times]
        y_values = [n for _, n in num_jobs_times]
        plt.figure(figsize=(10, 6))
        plt.step(x_values, y_values, where='post')
        plt.xlabel('Time')
    else:
        # Batch means
        x_values = list(range(1, len(num_jobs_times) + 1))
        y_values = num_jobs_times
        plt.figure(figsize=(10, 6))
        plt.plot(x_values, y_values, linestyle='-')
        plt.xlabel('Batch')

    plt.ylabel(ylabel)
    plt.grid(True)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'{name}.png')
    plt.savefig(output_path)
    plt.close()

# Funzione per stampare le statistiche della simulazione
def print_simulation_stats(stats, type):
    """
    Stampa le statistiche della simulazione.
    stats: oggetto contenente le metriche raccolte
    type: "replications" o "batch"
    """

    # Node A
    print(f"\nNode A - Average wait time: {statistics.mean(stats.A_avg_wait):.6f} ± {calculate_confidence_interval(stats.A_avg_wait):.6f}")
    print(f"Node A - Average service time: {statistics.mean(stats.A_avg_serv):.6f} ± {calculate_confidence_interval(stats.A_avg_serv):.6f}")
    print(f"Node A - Average response time: {statistics.mean(stats.A_avg_resp):.6f} ± {calculate_confidence_interval(stats.A_avg_resp):.6f}")
    print(f"Node A - Utilization: {statistics.mean(stats.A_utilization):.6f} ± {calculate_confidence_interval(stats.A_utilization):.6f}")
    print(f"Node A - Average number in node: {statistics.mean(stats.A_avg_num_job):.6f} ± {calculate_confidence_interval(stats.A_avg_num_job):.6f}")
    print(f"Node A - Throughput: {statistics.mean(stats.A_throughput):.6f} ± {calculate_confidence_interval(stats.A_throughput):.6f}")

    # Node B
    print(f"\nNode B - Average wait time: {statistics.mean(stats.B_avg_wait):.6f} ± {calculate_confidence_interval(stats.B_avg_wait):.6f}")
    print(f"Node B - Average service time: {statistics.mean(stats.B_avg_serv):.6f} ± {calculate_confidence_interval(stats.B_avg_serv):.6f}")
    print(f"Node B - Average response time: {statistics.mean(stats.B_avg_resp):.6f} ± {calculate_confidence_interval(stats.B_avg_resp):.6f}")
    print(f"Node B - Utilization: {statistics.mean(stats.B_utilization):.6f} ± {calculate_confidence_interval(stats.B_utilization):.6f}")
    print(f"Node B - Average number in node: {statistics.mean(stats.B_avg_num_job):.6f} ± {calculate_confidence_interval(stats.B_avg_num_job):.6f}")
    print(f"Node B - Throughput: {statistics.mean(stats.B_throughput):.6f} ± {calculate_confidence_interval(stats.B_throughput):.6f}")

    # Node P
    print(f"\nNode P - Average wait time: {statistics.mean(stats.P_avg_wait):.6f} ± {calculate_confidence_interval(stats.P_avg_wait):.6f}")
    print(f"Node P - Average service time: {statistics.mean(stats.P_avg_serv):.6f} ± {calculate_confidence_interval(stats.P_avg_serv):.6f}")
    print(f"Node P - Average response time: {statistics.mean(stats.P_avg_resp):.6f} ± {calculate_confidence_interval(stats.P_avg_resp):.6f}")
    print(f"Node P - Utilization: {statistics.mean(stats.P_utilization):.6f} ± {calculate_confidence_interval(stats.P_utilization):.6f}")
    print(f"Node P - Average number in node: {statistics.mean(stats.P_avg_num_job):.6f} ± {calculate_confidence_interval(stats.P_avg_num_job):.6f}")
    print(f"Node P - Throughput: {statistics.mean(stats.P_throughput):.6f} ± {calculate_confidence_interval(stats.P_throughput):.6f}")

    # Sub-nodes A1, A2, A3
    for i in [1, 2, 3]:
        print(f"\nNode A{i} - Average wait time: {statistics.mean(getattr(stats, f'A{i}_avg_wait')):.6f} ± {calculate_confidence_interval(getattr(stats, f'A{i}_avg_wait')):.6f}")
        print(f"Node A{i} - Average service time: {statistics.mean(getattr(stats, f'A{i}_avg_serv')):.6f} ± {calculate_confidence_interval(getattr(stats, f'A{i}_avg_serv')):.6f}")
        print(f"Node A{i} - Average response time: {statistics.mean(getattr(stats, f'A{i}_avg_resp')):.6f} ± {calculate_confidence_interval(getattr(stats, f'A{i}_avg_resp')):.6f}")

    # Metriche del sistema
    print(f"\nSystem - Average response time: {statistics.mean(stats.system_avg_response_time):.6f} ± {calculate_confidence_interval(stats.system_avg_response_time):.6f}")
    print(f"System - Average service time: {statistics.mean(stats.system_avg_service_time):.6f} ± {calculate_confidence_interval(stats.system_avg_service_time):.6f}")
    print(f"System - Average wait time: {statistics.mean(stats.system_avg_wait):.6f} ± {calculate_confidence_interval(stats.system_avg_wait):.6f}")
    print(f"System - Utilization: {statistics.mean(stats.system_utilization):.6f} ± {calculate_confidence_interval(stats.system_utilization):.6f}")
    print(f"System - Average number of jobs: {statistics.mean(stats.system_avg_num_job):.6f} ± {calculate_confidence_interval(stats.system_avg_num_job):.6f}")
    print(f"System - Throughput: {statistics.mean(stats.system_throughput):.6f} ± {calculate_confidence_interval(stats.system_throughput):.6f}")


# Grafico di validazione: confronta l'ampiezza dell'IC 95% dei tempi di risposta
# tra lo scenario baseline e lo scenario realistico (lambda variabile + iper-esponenziale).
# Legge le repliche già salvate nei CSV prodotti dalle rispettive simulazioni finite.
def plot_ci_width_comparison(baseline_csv="base_model_finite_results.csv",
                             realistic_csv="realistic_model_finite_results.csv",
                             name="ci_width_baseline_vs_realistic"):
    output_dir = "simulation/../output/plot/validation"
    os.makedirs(output_dir, exist_ok=True)

    centers = [
        ("A",      "A_avg_resp"),
        ("B",      "B_avg_resp"),
        ("P",      "P_avg_resp"),
        ("A1",     "A1_avg_resp"),
        ("A2",     "A2_avg_resp"),
        ("A3",     "A3_avg_resp"),
        ("System", "system_avg_response_time"),
    ]

    def _read_column(path, col):
        values = []
        with open(path, "r", newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    values.append(float(row[col]))
                except (KeyError, ValueError):
                    continue
        return values

    base_path = file_path + baseline_csv
    real_path = file_path + realistic_csv

    if not os.path.exists(base_path) or not os.path.exists(real_path):
        print(f"[plot_ci_width_comparison] CSV mancanti: {base_path} o {real_path}")
        return

    labels = []
    base_widths = []
    real_widths = []
    for label, col in centers:
        base_vals = _read_column(base_path, col)
        real_vals = _read_column(real_path, col)
        if not base_vals or not real_vals:
            continue
        labels.append(label)
        base_widths.append(calculate_confidence_interval(base_vals))
        real_widths.append(calculate_confidence_interval(real_vals))

    x = list(range(len(labels)))
    width = 0.38

    plt.figure(figsize=(10, 6))
    plt.bar([i - width/2 for i in x], base_widths, width,
            label="Baseline (Poisson)", color="#4C78A8")
    plt.bar([i + width/2 for i in x], real_widths, width,
            label="Realistic (variable λ + hyperexponential)", color="#E45756")

    plt.xticks(x, labels)
    plt.ylabel("95% CI half-width on mean response time [s]")
    plt.title("CI width comparison: baseline vs realistic scenario")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    for i, (b, r) in enumerate(zip(base_widths, real_widths)):
        plt.text(i - width/2, b, f"{b:.3g}", ha="center", va="bottom", fontsize=8)
        plt.text(i + width/2, r, f"{r:.3g}", ha="center", va="bottom", fontsize=8)

    output_path = os.path.join(output_dir, f"{name}.png")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"[plot_ci_width_comparison] Salvato in {output_path}")
