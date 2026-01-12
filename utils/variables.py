K = 128
B = 4080

INFINITE = 0
FINITE = 1
SIM_TYPE = FINITE

INFINITY = float('inf')

LAMBDA = 1.2 # arrival rate



# LAMBDA_SIN_AMP = 0.3      # ampiezza del seno
# LAMBDA_PERIOD = 60000     # periodo del seno

# SPIKE_CENTER = 41000      # centro dello spike
# SPIKE_SIGMA = 1000        # larghezza del picco

# SPIKE_HEIGHT = 0.9        # altezza del picco
# LAMBDA_MAX = LAMBDA + LAMBDA_SIN_AMP + SPIKE_HEIGHT      # valore massimo di lambda durante la simulazione  


LAMBDA_SIN_AMP = 0.3     # sinusoide: 1.2 ± 0.3  -> range ~[0.9, 1.5]
LAMBDA_PERIOD = 60000.0  # periodo della sinusoide

#Picco anomalo 
LAMBDA_SPIKE_START = 40000.0  # inizio picco
LAMBDA_SPIKE_END   = 42000.0  # fine picco
LAMBDA_SPIKE_HEIGHT = 0.9  # durante il picco aggiunge +0.9 -> max ~2.4

#clamp per evitare valori assurdi
LAMBDA_MIN = 1e-6


BASE = 1
MODEL = BASE

START = 0.0
STOP = 100000 #86400  # terminal (close the door) time
STOP_ANALYSIS = 300000
STOP_INFINITE = float('inf')

SEED = 123456789

REPLICATIONS = 10

TRANSIENT_ANALYSIS = 0  # 1 per fare l'analisi del transitorio, 0 per simulazioni finite/infinite normali

PRINT_PLOT_BATCH = 1

# --- PARAMETRI DI SCALING ---
SImax = 8 
MIN_SERVERS = 1
MAX_SERVERS = 2 #calcolato analiticamente 
RHO_UP = 0.8 #rho target per scalare up
RHO_DOWN = 0.5 #rho target per scalare down
BASE_MU_LAYER1 = 1.25     # 1 / mean service time
BASE_MU_SPIKE = 1.875      # spike più veloce (vertical scaling) -> 1.25 * k = 1.25 * 1.5 perche k > 1
LAMBDA_NORMAL_MAX = 1.5   # dato che la sinusoide va 0.9 → 1.5
ANOM_EPS = 0.05  # tolleranza per rilevamento anomalia

def set_simulation(model, type):
    global SIM_TYPE, MODEL 
    if model == 1:
        MODEL = BASE
    if type == 1: 
        SIM_TYPE == FINITE 
    else: 
        SIM_TYPE = INFINITE
    