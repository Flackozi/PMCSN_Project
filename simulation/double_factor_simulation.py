import utils.variables as vs
from utils.sim_utils import*
from utils.sim_output import *
from libraries.rngs import *
from utils.sim_stats import*
from utils.variables import *
from libraries.rngs import *
from simulation.simulator import finite_simulation
import simulation.simulator as sim



def finite_2fa_simulation(stop, seed):
    """
    Runs a finite simulation with Two-Factor Authentication enabled.
    """

    # Patch del servizio P
    sim.get_service_P = sim.get_service_P_2FA

    # Patch del servizio A per job di classe 3
    sim.get_service_A = sim.get_service_A_2FA

    # Avvio simulazione
    results, stats = finite_simulation(stop, seed)

    # Ripristino comportamento originale
    sim.get_service_P = get_service_P
    sim.get_service_A = get_service_A

    print("\n[INFO] 2FA simulation completed\n")

    return results, stats


