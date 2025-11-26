K = 128
B = 4000

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

MU_A = 2.0  # service rate at A
MU_B = 1.0  # service rate at B
MU_P = 0.5  # service rate at P (delay center)

PRINT_PLOT_BATCH = 1


def set_simulation(model, type):
    global SIM_TYPE, MODEL 
    if model == 1:
        MODEL = BASE
    if type == 1: 
        SIM_TYPE == FINITE 
    else: 
        SIM_TYPE = INFINITE
    