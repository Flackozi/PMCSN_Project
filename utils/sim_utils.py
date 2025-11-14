import utils.variables as vs
import math
from math import log
from libraries import rvms
from libraries.rngs import selectStream, random
import statistics

arrivalTemp = vs.START

def get_simulation(model):
    # print("Select model:")
    # print("1. Base model")
    # # print("2. Better")
    # # print("3. Standard Scalability")
    # # print("4. Better Scalability")
    # model = int(input("Select the number: "))

    # if model < 1 or model > 4:
    #     raise ValueError()

    # if model == 3 or model == 4:
    #     sim = 1
    # else:
    print("Select simulation:")
    print("1. Finite")
    print("2. Infinite")
    sim = int(input("Select the number: "))

    if sim < 1 or sim > 2:
        raise ValueError()

    
    vs.set_simulation(model, sim)



def reset_arrival_temp():
    global arrivalTemp
    arrivalTemp = vs.START

def Exponential(m):
    """Generate an Exponential random variate, use m > 0.0."""
    return -m * log(1.0 - random())

def GetArrival():
    """Generate the next arrival time for the first server."""
    global arrivalTemp
    selectStream(0)
    arrivalTemp += Exponential(1 / vs.LAMBDA)
    return arrivalTemp

def get_service_A(classe):
    if classe == 1:
        selectStream(1)
        return 0.2
    elif classe == 2:
        selectStream(2)
        return 0.4
    else: 
        selectStream(3)
        return 0.1


def get_service_B():
    selectStream(2)
    return 0.8

def get_service_P():
    selectStream(3)
    return 0.4

def append_stats(replicationStats, results, stats):
    """
    Salva, per una replica, tutti i valori contenuti in `results`
    (cioè in return_stats) dentro replicationStats.metrics.

    Esempio:
      results["A_avg_wait"] -> replicationStats.metrics["A_avg_wait"].append(...)
    """
    for key, value in results.items():
        replicationStats.metrics[key].append(value)

    replicationStats.A_wait_interval.append(stats.A_wait_times)
    replicationStats.B_wait_interval.append(stats.B_wait_times)
    replicationStats.A1_wait_interval.append(stats.A1_wait_times)
    replicationStats.A2_wait_interval.append(stats.A2_wait_times)
    replicationStats.A3_wait_interval.append(stats.A3_wait_times)

    replicationStats.A_resp_interval.append(stats.A_resp_times)
    replicationStats.B_resp_interval.append(stats.B_resp_times)
    replicationStats.A1_resp_interval.append(stats.A1_resp_times)
    replicationStats.A2_resp_interval.append(stats.A2_resp_times)
    replicationStats.A3_resp_interval.append(stats.A3_resp_times)
    
