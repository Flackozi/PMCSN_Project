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

def remove_batch(stats, n):
    if n < 0:
        raise ValueError()
    for attr in dir(stats):
        value = getattr(stats, attr)
        if isinstance(value, list):
            setattr(stats, attr, value[n:])

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

def get_service_spike():
    return Exponential(1 / vs.BASE_MU_SPIKE)

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

    """
    replicationStats.system_avg_wait.append(results['system_avg_wait'])
    replicationStats.system_avg_response_time.append(results['system_avg_response_time'])   
    replicationStats.system_avg_service_time.append(results['system_avg_service_time'])
    replicationStats.system_utilization.append(results['system_utilization'])

    replicationStats.A_avg_wait.append(results['A_avg_wait'])
    replicationStats.A_avg_resp.append(results['A_avg_resp'])
    replicationStats.A_avg_serv.append(results['A_avg_serv'])
    replicationStats.A_utilization.append(results['A_utilization'])
    replicationStats.A_avg_num_job.append(results['A_avg_num_job'])

    replicationStats.B_avg_wait.append(results['B_avg_wait'])
    replicationStats.B_avg_serv.append(results['B_avg_serv'])
    replicationStats.B_avg_resp.append(results['B_avg_resp'])
    replicationStats.B_utilization.append(results['B_utilization'])
    replicationStats.B_avg_num_job.append(results['B_avg_num_job'])

    replicationStats.A1_avg_wait.append(results['A1_avg_wait'])
    replicationStats.A1_avg_resp.append(results['A1_avg_resp'])
    replicationStats.A1_avg_serv.append(results['A1_avg_serv'])

    replicationStats.A2_avg_wait.append(results['A2_avg_wait'])
    replicationStats.A2_avg_resp.append(results['A2_avg_resp'])
    replicationStats.A2_avg_serv.append(results['A2_avg_serv'])

    replicationStats.A3_avg_wait.append(results['A3_avg_wait'])
    replicationStats.A3_avg_resp.append(results['A3_avg_resp'])
    replicationStats.A3_avg_serv.append(results['A3_avg_serv'])  

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
    
