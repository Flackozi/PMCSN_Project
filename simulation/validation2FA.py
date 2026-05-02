import statistics
import csv
import os
import matplotlib.pyplot as plt

import utils.variables as vs
from utils.variables import STOP_INFINITE, SEED
from libraries.rngs import plantSeeds
import simulation.simulator as sim
from simulation.simulator import infinite_simulation

_LAMBDA_GRID = [round(0.5 + i * 0.05, 2) for i in range(15)]  # 0.50 ... 1.20 (15 punti)
_WARMUP_BATCHES = 5  # coerente con start_infinite_simulation (remove_batch(5))

_CSV_PATH   = "simulation/../output/csv/validation2FA.csv"
_PLOT_NAVG  = "simulation/../output/plot/validation2FA_Navg.png"
_PLOT_RT    = "simulation/../output/plot/validation2FA_RT.png"


def _run_one(lam: float, two_fa: bool):
    """
    Simulazione a orizzonte infinito (K=128 batch, B=4080 job/batch) con λ fisso.
    Restituisce (N_avg, RT_avg) come medie sui batch effettivi (dopo warmup).
    """
    vs.LAMBDA = lam
    plantSeeds(SEED)

    if two_fa:
        sim.get_service_A = sim.get_service_A_2FA
        sim.get_service_P = sim.get_service_P_2FA
    else:
        sim.get_service_A = _orig_service_A
        sim.get_service_P = _orig_service_P

    _, batch_stats, _ = infinite_simulation(STOP_INFINITE)

    n_vals  = batch_stats.system_avg_num_job[_WARMUP_BATCHES:]
    rt_vals = batch_stats.system_avg_response_time[_WARMUP_BATCHES:]

    n_avg  = statistics.mean(n_vals)  if n_vals  else float('nan')
    rt_avg = statistics.mean(rt_vals) if rt_vals else float('nan')
    return n_avg, rt_avg


_orig_service_A = None
_orig_service_P = None


def run_validation2FA():
    global _orig_service_A, _orig_service_P

    _orig_lambda    = vs.LAMBDA
    _orig_service_A = sim.get_service_A
    _orig_service_P = sim.get_service_P

    results = []

    for lam in _LAMBDA_GRID:
        print(f"[validation2FA] λ={lam:.2f} — 1FA ...", flush=True)
        n_1fa, rt_1fa = _run_one(lam, two_fa=False)

        print(f"[validation2FA] λ={lam:.2f} — 2FA ...", flush=True)
        n_2fa, rt_2fa = _run_one(lam, two_fa=True)

        print(f"  → N_1FA={n_1fa:.3f}  N_2FA={n_2fa:.3f}  RT_1FA={rt_1fa:.3f}s  RT_2FA={rt_2fa:.3f}s", flush=True)
        results.append((lam, n_1fa, n_2fa, rt_1fa, rt_2fa))

    vs.LAMBDA          = _orig_lambda
    sim.get_service_A  = _orig_service_A
    sim.get_service_P  = _orig_service_P

    _save_csv(results)
    _save_navg_plot(results)
    _save_rt_plot(results)
    print("[validation2FA] Completata.")


def _save_csv(results):
    os.makedirs(os.path.dirname(_CSV_PATH), exist_ok=True)
    with open(_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["lambda", "N_avg_one_factor", "N_avg_two_factor",
                         "RT_avg_one_factor", "RT_avg_two_factor"])
        for lam, n1, n2, rt1, rt2 in results:
            writer.writerow([f"{lam:.2f}", f"{n1:.6f}", f"{n2:.6f}",
                             f"{rt1:.6f}", f"{rt2:.6f}"])
    print(f"[validation2FA] CSV → {_CSV_PATH}")


def _save_navg_plot(results):
    lambdas = [r[0] for r in results]
    n_1fa   = [r[1] for r in results]
    n_2fa   = [r[2] for r in results]
    _make_plot(lambdas, n_1fa, n_2fa,
               ylabel="Numero medio di job nel sistema",
               title="Numero medio di job nel sistema vs λ",
               path=_PLOT_NAVG, ylim=None)


def _save_rt_plot(results):
    lambdas = [r[0] for r in results]
    rt_1fa  = [r[3] for r in results]
    rt_2fa  = [r[4] for r in results]
    _make_plot(lambdas, rt_1fa, rt_2fa,
               ylabel="Tempo medio di risposta [s]",
               title="Tempo medio di risposta vs λ",
               path=_PLOT_RT, ylim=(0, 50))


def _make_plot(lambdas, y_1fa, y_2fa, ylabel, title, path, ylim):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(lambdas, y_1fa, color="tab:blue",   marker="o", linewidth=1.8, label="One-Factor")
    ax.plot(lambdas, y_2fa, color="tab:orange", marker="o", linewidth=1.8, label="Two-Factor")
    ax.set_xlabel("λ (req/s)", fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=13)
    ax.legend(loc="upper left", fontsize=11)
    ax.grid(True)
    ax.set_xlim(0.48, 1.22)
    if ylim is not None:
        ax.set_ylim(*ylim)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[validation2FA] Plot → {path}")
