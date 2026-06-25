import traceback

import utils.variables as vs
from simulation.realistic_2fa_simulator import realistic_2fa_finite_simulation
from simulation.realistic_simulator import realistic_finite_simulation
from simulation.scaling_2fa_simulation import scaling_2fa_finite_simulation
from simulation.scaling_simulator import scaling_finite_simulation
from simulation.simulator import finite_simulation, infinite_simulation
from utils.sim_output import (
    clear_file,
    plot_active_servers_t,
    plot_analysis,
    plot_batch,
    plot_ci_width_comparison,
    plot_lambda_t,
    plot_num_jobs_t,
    plot_realistic_vs_scaling_response_time,
    plot_replication_response_times,
    plot_rho_t,
    plot_spike_active_t,
    print_simulation_stats,
    write_file,
)
from utils.sim_stats import ReplicationStats
from utils.sim_utils import append_stats, remove_batch


RESPONSE_SERIES = (
    ("A_resp_interval", "A"),
    ("B_resp_interval", "B"),
    ("P_resp_interval", "P"),
    ("A1_resp_interval", "A1"),
    ("A2_resp_interval", "A2"),
    ("A3_resp_interval", "A3"),
)


def _finite_settings(csv_stem, normal_replications=50):
    if vs.TRANSIENT_ANALYSIS == 1:
        vs.REPLICATIONS = 10
        return vs.STOP_ANALYSIS, f"{csv_stem}_transient_analysis_results.csv", True

    vs.REPLICATIONS = normal_replications
    return vs.STOP, f"{csv_stem}_finite_results.csv", False


def _run_replications(label, simulation_fn, stop, file_name):
    print(label)
    clear_file(file_name)

    replication_stats = ReplicationStats()
    last_stats = None

    for i in range(vs.REPLICATIONS):
        print(f"start {label.lower()} replication {i + 1}")
        results, last_stats = simulation_fn(stop)
        print(f"end {label.lower()} replication {i + 1}")
        write_file(results, file_name)
        append_stats(replication_stats, results, last_stats)

    return replication_stats, last_stats


def _plot_response_stats(replication_stats, sim_type, transient):
    for attr, name in RESPONSE_SERIES:
        values = getattr(replication_stats, attr)
        if transient:
            plot_analysis(values, replication_stats.seed, name, sim_type)
        else:
            plot_replication_response_times(values, sim_type, name)


def _plot_system_response_stats(replication_stats, sim_type, transient):
    if transient:
        plot_analysis(replication_stats.system_resp_interval, replication_stats.seed, "system_resp_t", sim_type)
    else:
        plot_replication_response_times(replication_stats.system_resp_interval, sim_type, "system_resp_t")


def _plot_num_jobs(stats, sim_type):
    plot_num_jobs_t(stats.Nsys_times, sim_type, "Nsys", ylabel="N system")
    plot_num_jobs_t(stats.NA_times, sim_type, "NA", ylabel="N A")
    plot_num_jobs_t(stats.NB_times, sim_type, "NB", ylabel="N B")
    plot_num_jobs_t(stats.NP_times, sim_type, "NP", ylabel="N P")


def _plot_scaling_series(stats, sim_type):
    plot_lambda_t(stats.lambda_times, sim_type, "lambda_t")
    plot_active_servers_t(stats.layer0_servers_times, sim_type, "servers_A_t", ylabel="Active servers (A)")
    plot_active_servers_t(stats.layer1_servers_times, sim_type, "servers_B_t", ylabel="Active servers (B)")
    plot_rho_t(stats.rhoA_samples, sim_type, "rho_A_t", ylabel="Rho A")
    plot_rho_t(stats.rhoB_samples, sim_type, "rho_B_t", ylabel="Rho B")
    plot_spike_active_t(stats.spike_active_times, sim_type, "spike_B_active_t", ylabel="Spike B active (0/1)")
    plot_spike_active_t(stats.spike_A_active_times, sim_type, "spike_A_active_t", ylabel="Spike A active (0/1)")


def _start_finite_scenario(
    label,
    simulation_fn,
    csv_stem,
    plot_stem,
    normal_replications=50,
    plot_population=True,
    plot_scaling=False,
):
    stop, file_name, transient = _finite_settings(csv_stem, normal_replications)
    replication_stats, stats = _run_replications(label, simulation_fn, stop, file_name)

    if plot_scaling:
        folder = "transient_analysis" if transient else "finite_simulation"
        _plot_scaling_series(stats, f"{folder}/{plot_stem}")

    _plot_response_stats(replication_stats, plot_stem, transient)
    _plot_system_response_stats(replication_stats, plot_stem, transient)

    if plot_population and not transient:
        _plot_num_jobs(stats, f"finite_simulation/{plot_stem}")

    return replication_stats, stats


def start_base_simulation():
    start_infinite_base_simulation()


def start_infinite_base_simulation():
    file_name = "base_model_infinite_results.csv"
    print("INFINITE BASE SIMULATION")
    clear_file(file_name)

    rep_stats, batch_stats, _ = infinite_simulation(vs.STOP_INFINITE)
    print("End infinite base simulation")

    for results in rep_stats:
        write_file(results, file_name)

    remove_batch(batch_stats, 5)

    if vs.PRINT_PLOT_BATCH == 1:
        plot_batch(batch_stats.system_avg_response_time, "base_model", "system")
        plot_batch(batch_stats.A_avg_resp, "base_model", "center_A")
        plot_batch(batch_stats.B_avg_resp, "base_model", "center_B")
        plot_batch(batch_stats.P_avg_resp, "base_model", "center_P")
        plot_batch(batch_stats.A1_avg_resp, "base_model", "class_1_A")
        plot_batch(batch_stats.A2_avg_resp, "base_model", "class_2_A")
        plot_batch(batch_stats.A3_avg_resp, "base_model", "class_3_A")

        sim_type = "infinite_simulation/base_model"
        plot_num_jobs_t(batch_stats.A_avg_num_job, sim_type, "num_jobs_A", ylabel="Average number of jobs in A")
        plot_num_jobs_t(batch_stats.B_avg_num_job, sim_type, "num_jobs_B", ylabel="Average number of jobs in B")
        plot_num_jobs_t(batch_stats.P_avg_num_job, sim_type, "num_jobs_P", ylabel="Average number of jobs in P")
        plot_num_jobs_t(
            batch_stats.system_avg_num_job,
            sim_type,
            "num_jobs_system",
            ylabel="Average number of jobs in system",
        )

    print_simulation_stats(batch_stats, "replications")


def start_realistic_simulation():
    _start_finite_scenario(
        "FINITE REALISTIC SIMULATION",
        realistic_finite_simulation,
        "realistic_model",
        "realistic_model",
    )


def start_realistic_2fa_simulation():
    _start_finite_scenario(
        "FINITE REALISTIC 2FA SIMULATION",
        realistic_2fa_finite_simulation,
        "realistic_2fa_model",
        "realistic_2fa_model",
    )


def start_scaling_simulation():
    _, scaling_stats = _start_finite_scenario(
        "FINITE SCALING REALISTIC SIMULATION",
        scaling_finite_simulation,
        "scaling_model",
        "scaling_model",
        normal_replications=1,
        plot_population=False,
        plot_scaling=True,
    )
    if vs.TRANSIENT_ANALYSIS != 1:
        _, realistic_stats = realistic_finite_simulation(vs.STOP)
        plot_realistic_vs_scaling_response_time(
            realistic_stats.system_resp_times,
            scaling_stats.system_resp_times,
            qos=10.0,
        )


def start_scaling_2fa_simulation():
    _start_finite_scenario(
        "FINITE SCALING REALISTIC 2FA SIMULATION",
        scaling_2fa_finite_simulation,
        "scaling_2fa_model",
        "scaling_2fa_model",
        plot_population=False,
        plot_scaling=True,
    )


def start_ci_validation_comparison():
    try:
        vs.REPLICATIONS = 50

        base_replication_stats, base_stats = _run_replications(
            "FINITE BASE SIMULATION (validation run)",
            finite_simulation,
            vs.STOP,
            "base_model_finite_results.csv",
        )
        _plot_response_stats(base_replication_stats, "base_model", transient=False)
        _plot_system_response_stats(base_replication_stats, "base_model", transient=False)
        _plot_num_jobs(base_stats, "finite_simulation/base_model")

        realistic_replication_stats, realistic_stats = _run_replications(
            "FINITE REALISTIC SIMULATION (validation run)",
            realistic_finite_simulation,
            vs.STOP,
            "realistic_model_finite_results.csv",
        )
        _plot_response_stats(realistic_replication_stats, "realistic_model", transient=False)
        _plot_system_response_stats(realistic_replication_stats, "realistic_model", transient=False)
        _plot_num_jobs(realistic_stats, "finite_simulation/realistic_model")

        plot_ci_width_comparison(
            baseline_csv="base_model_finite_results.csv",
            realistic_csv="realistic_model_finite_results.csv",
        )
    except Exception:
        print("Error during CI validation comparison:")
        traceback.print_exc()


def start():
    print("1. Base model infinite simulation")
    print("2. Realistic base model finite simulation (hyperexponential + variable lambda)")
    print("3. Realistic base model + 2FA finite simulation")
    print("4. Improved model finite simulation (scaling + realistic arrivals)")
    print("5. Improved model + 2FA finite simulation (scaling + realistic arrivals)")
    print("6. Validation: CI width comparison with finite baseline and finite realistic simulations")

    try:
        choice = int(input("Select the type: "))
    except ValueError:
        print("Invalid choice.")
        return

    actions = {
        1: start_base_simulation,
        2: start_realistic_simulation,
        3: start_realistic_2fa_simulation,
        4: start_scaling_simulation,
        5: start_scaling_2fa_simulation,
        6: start_ci_validation_comparison,
    }

    action = actions.get(choice)
    if action is None:
        print("Invalid choice.")
        return

    action()


if __name__ == "__main__":
    start()
