import utils.variables as vs
from  utils.sim_utils import get_simulation

def start_simulation():
    if vs.SIM_TYPE == FINITE:
        res = start_finite_sim()
    elif vs.SIM_TYPE == INFINITE:
        res = start_infinite_sim()
    else:
        print("Type not valid")
        exit(1)
    return res

def start_finite_sim():
    


def start():
    print("1. Base model simulation")
    print("2. Base model + 2FA simulation")
    try:
        choice = int(input("Select the type: "))
        if choice == 1:
            get_simulation()
            start_simulation()
    except ValueError:
        print("Error: invalid choice.")    

start()            