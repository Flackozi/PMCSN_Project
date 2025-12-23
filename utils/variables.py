K = 128
B = 4080

INFINITE = 0
FINITE = 1
SIM_TYPE = FINITE

INFINITY = float('inf')

LAMBDA = 1.2 # arrival rate

BASE = 1
MODEL = BASE

START = 0.0
STOP = 10000 #86400  # terminal (close the door) time
STOP_ANALYSIS = 300000
STOP_INFINITE = float('inf')

SEED = 123456789

REPLICATIONS = 10

PRINT_PLOT_BATCH = 1

# --- PARAMETRI DI SCALING ---
SImax = 70 #calcolato analiticamente usando la distribuzione geometrica
MIN_SERVERS = 1
MAX_SERVERS = 2 #calcolato analiticamente 
RHO_UP = 0.8 #rho target per scalare up
RHO_DOWN = 0.3 #rho target per scalare down
BASE_MU_LAYER1 = 1.25     # 1 / mean service time
BASE_MU_SPIKE = 1.875      # spike più veloce (vertical scaling) -> 1.25 * k = 1.25 * 1.5 perche k > 1


def set_simulation(model, type):
    global SIM_TYPE, MODEL 
    if model == 1:
        MODEL = BASE
    if type == 1: 
        SIM_TYPE == FINITE 
    else: 
        SIM_TYPE = INFINITE
    