INFINITE = 0
FINITE =1
BASE = 1
def set_simulation(model, type):
    global SIM_TYPE, MODEL 
    if model == 1:
        MODEL = BASE
    elif type == 1: 
        SIM_TYPE == FINITE 
    else: 
        SIM_TYPE = INFINITE
    