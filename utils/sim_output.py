import csv
import statistics
import matplotlib.pyplot as plt
import os

file_path = "simulation/../output/"

header = ['seed', 'A_avg_resp', 'A_avg_wait', 'A_avg_serv', 'A_utilization', 'A_avg_num_job', 'B_avg_resp',
          'B_avg_wait', 'B_avg_serv', 'B_utilization', 'B_avg_num_job', 'A1_avg_resp', 'A1_avg_wait', 'A1_avg_serv', 'A2_avg_resp',
          'A2_avg_wait', 'A2_avg_serv', 'A3_avg_resp', 'A3_avg_wait', 'A3_avg_serv', 'total_completed', 'system_avg_response_time', 
          'system_avg_service_time', 'system_utilization', 'system_avg_wait', 'job_arrived', 'completions_A1', 'completions_A2',
          'completions_A3', 'completions_B', 'completions_P', 'horizon']

def write_file(results, file_name):
    path = file_path + file_name
    with open(path, "a", newline = '', encoding='utf-8') as csvfile:
        write = csv.DictWriter(csvfile, fieldnames=header)
        write.writerow(results)

def clear_file(file_name):
    path = file_path + file_name
    with open(path, "w", newline = '', encoding='utf-8') as csvfile:
        write = csv.DictWriter(csvfile, fieldnames=header)
        write.writeheader()

def plot_batch(wait_times, sim_type, name):
    output_dir = f"simulation/../output/plot/batch/{sim_type}"

    x_values = [index for index in range(len(wait_times)+1)]
    y_values = [0]
    for i in range(len(wait_times)):
        y_values.append(statistics.mean(wait_times[:i+1]))

    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, linestyle='-', color='b')
    plt.xlabel('Batch')
    plt.ylabel('Wait time')
    plt.grid(True)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'{name}.png')
    plt.savefig(output_path)
    plt.close()


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

