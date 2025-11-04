
INFINITE = 0
FINITE = 1
SIM_TYPE = FINITE

INFINITY = float('inf')


BASE = 1
MODEL = BASE

START = 0.0
STOP = 86400  # terminal (close the door) time
STOP_ANALYSIS = 300000

SEED = 123456789

REPLICATIONS = 96



def set_simulation(model, type):
    global SIM_TYPE, MODEL 
    if model == 1:
        MODEL = BASE
    if type == 1: 
        SIM_TYPE == FINITE 
    else: 
        SIM_TYPE = INFINITE
    