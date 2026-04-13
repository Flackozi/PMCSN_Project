import simulation.simulator_base_variabile as sbv
from simulation.simulator_base_variabile import finite_simulation


def finite_2fa_variabile_simulation(stop):

    # Patch del servizio P con tempi 2FA
    sbv.get_service_P = sbv.get_service_P_2FA

    # Patch del servizio A con tempi 2FA
    sbv.get_service_A = sbv.get_service_A_2FA

    results, stats = finite_simulation(stop)

    print("\n[INFO] 2FA + variable lambda simulation completed\n")

    return results, stats
