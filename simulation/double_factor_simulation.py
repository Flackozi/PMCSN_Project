# realizzo la simulazione con l'introduzione dell'autenticazione a due fattori (2FA)
import utils.variables as vs
import traceback
from utils.sim_utils import*
from utils.sim_output import *
from libraries.rngs import *
from utils.sim_stats import*
from utils.variables import *
import math
from libraries.rngs import *
from simulation.simulator import finite_simulation
import simulation.simulator as sim



# ============================
# 2FA CONFIGURATION
# ============================

# Moltiplicatore del tempo di servizio di P
# (nel PDF è significativamente più alto del caso 1FA)
#TWO_FA_FACTOR = 2.0


# ============================
# 2FA SERVICE PATCH
# ============================

#_original_get_service_P = sim.get_service_P_2FA


# def get_service_P_2fa():
#     """
#     Two-Factor Authentication service time.
#     Models an external strong authentication provider.
#     """

#     print("[DEBUG] get_service_P_2fa called")
#     return sim.get_service_P_2FA()

# def get_service_A_2fa():
#     """
#     Two-Factor Authentication service time.
#     Models an external strong authentication provider.
#     """

#     print("[DEBUG] get_service_P_2fa called")
#     return sim.get_service_P_2FA()

# ============================
# MAIN 2FA SIMULATION
# ============================

def finite_2fa_simulation(stop, seed):
    """
    Runs a finite simulation with Two-Factor Authentication enabled.
    """



    # Patch del servizio P
    sim.get_service_P = sim.get_service_P_2FA

    # Patch del servizio A per job di classe 3
    sim.get_service_A = sim.get_service_A_2FA

    #print(f"[INFO] 2FA enabled → Service time of P multiplied by {TWO_FA_FACTOR}")

    # Avvio simulazione
    results, stats = finite_simulation(stop, seed)

    # Ripristino comportamento originale
    sim.get_service_P = get_service_P
    sim.get_service_A = get_service_A

    print("\n[INFO] 2FA simulation completed\n")

    return results, stats


