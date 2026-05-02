import csv
import os
import matplotlib.pyplot as plt

import utils.variables as vs
from utils.variables import SEED, STOP
from libraries.rngs import plantSeeds
import simulation.scaling_simulator as scal

_LAMBDA_GRID = [round(0.5 + i * 0.05, 2) for i in range(15)]  # 0.50 ... 1.20 (15 punti)

_CSV_PATH   = "simulation/../output/csv/validation2FAscaling.csv"
_PLOT_NAVG  = "simulation/../output/plot/validation2FAscaling_Navg.png"
_PLOT_RT    = "simulation/../output/plot/validation2FAscaling_RT.png"


def _run_one(lam: float, two_fa: bool):
    """
    Esegue una replica finita della simulazione scaling con λ base fisso a `lam`.
    La logica di arrivo è iper-esponenziale + sinusoide centrata su vs.LAMBDA,
    identica a start_scaling_sim (REPLICATIONS=1, stop=STOP).
    Restituisce (N_avg, RT_avg).
    """
    vs.LAMBDA = lam
    plantSeeds(SEED)

    if two_fa:
        scal.get_service_A = scal.get_service_A_2FA
        scal.get_service_P = scal.get_service_P_2FA
    else:
        scal.get_service_A = _orig_service_A
        scal.get_service_P = _orig_service_P

    results, _ = scal.scaling_finite_simulation(STOP)
    return results['system_avg_num_job'], results['system_avg_response_time']


_orig_service_A = None
_orig_service_P = None


def run_validation2FAscaling():
    global _orig_service_A, _orig_service_P

    _orig_lambda    = vs.LAMBDA
    _orig_service_A = scal.get_service_A
    _orig_service_P = scal.get_service_P

    data = []

    for lam in _LAMBDA_GRID:
        print(f"[validation2FAscaling] λ={lam:.2f} — 1FA ...", flush=True)
        n_1fa, rt_1fa = _run_one(lam, two_fa=False)

        print(f"[validation2FAscaling] λ={lam:.2f} — 2FA ...", flush=True)
        n_2fa, rt_2fa = _run_one(lam, two_fa=True)

        print(f"  → N_1FA={n_1fa:.3f}  N_2FA={n_2fa:.3f}  RT_1FA={rt_1fa:.3f}s  RT_2FA={rt_2fa:.3f}s", flush=True)
        data.append((lam, n_1fa, n_2fa, rt_1fa, rt_2fa))

    vs.LAMBDA          = _orig_lambda
    scal.get_service_A = _orig_service_A
    scal.get_service_P = _orig_service_P

    _save_csv(data)
    _save_navg_plot(data)
    _save_rt_plot(data)
    print("[validation2FAscaling] Completata.")


def _save_csv(data):
    os.makedirs(os.path.dirname(_CSV_PATH), exist_ok=True)
    with open(_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["lambda", "N_avg_one_factor", "N_avg_two_factor",
                         "RT_avg_one_factor", "RT_avg_two_factor"])
        for lam, n1, n2, rt1, rt2 in data:
            writer.writerow([f"{lam:.2f}", f"{n1:.6f}", f"{n2:.6f}",
                             f"{rt1:.6f}", f"{rt2:.6f}"])
    print(f"[validation2FAscaling] CSV → {_CSV_PATH}")


def _save_navg_plot(data):
    lambdas = [r[0] for r in data]
    n_1fa   = [r[1] for r in data]
    n_2fa   = [r[2] for r in data]
    _make_plot(lambdas, n_1fa, n_2fa,
               ylabel="Numero medio di job nel sistema",
               title="Numero medio di job nel sistema vs λ (Scaling)",
               path=_PLOT_NAVG, ylim=None, tag="validation2FAscaling")


def _save_rt_plot(data):
    lambdas = [r[0] for r in data]
    rt_1fa  = [r[3] for r in data]
    rt_2fa  = [r[4] for r in data]
    _make_plot(lambdas, rt_1fa, rt_2fa,
               ylabel="Tempo medio di risposta [s]",
               title="Tempo medio di risposta vs λ (Scaling)",
               path=_PLOT_RT, ylim=(0, 50), tag="validation2FAscaling")


def _make_plot(lambdas, y_1fa, y_2fa, ylabel, title, path, ylim, tag):
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
    print(f"[{tag}] Plot → {path}")
