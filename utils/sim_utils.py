import utils.variables as vs
import math
from math import log
from libraries import rvms
from libraries.rngs import selectStream, random
import statistics
import matplotlib.pyplot as plt

arrivalTemp = vs.START
arrivalTempScaling = vs.START

def get_simulation(model):
    
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
    
def reset_arrival_temp_scaling():
    global arrivalTempScaling
    arrivalTempScaling = vs.START

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


def get_service_A_2FA(classe):
    if classe == 1:
        selectStream(1)
        return 0.2
    elif classe == 2:
        selectStream(2)
        return 0.4
    else: 
        selectStream(6)
        return 0.15

def get_service_P_2FA():
    selectStream(5)
    return 0.7  


def append_stats(replicationStats, results, stats):
    """
    Salva, per una replica, tutti i valori contenuti in `results`
    (cioè in return_stats) dentro replicationStats.metrics.

    """
    replicationStats.seed.append(results['seed'])
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



def lambda_scaling(t: float) -> float:
    """
    Lambda variabile:
    sinusoide attorno a vs.LAMBDA.
    """
    base = vs.LAMBDA + vs.LAMBDA_SIN_AMP * math.sin(2 * math.pi * t / vs.LAMBDA_PERIOD)

    spike = 0.0
    if vs.LAMBDA_SPIKE_START <= t <= vs.LAMBDA_SPIKE_END:
        spike = vs.LAMBDA_SPIKE_HEIGHT

    lam = base + spike
    return max(lam, vs.LAMBDA_MIN)



def GetArrivalScaling(current_time: float) -> float:
    """
    Al tempo corrente 'current_time' calcolo lambda_scaling(current_time),
    poi genero il prossimo inter-arrivo come Exp(mean = 1/lambda).
    """
    global arrivalTempScaling
    selectStream(4)

    lam = lambda_scaling(current_time)
    inter = Exponential(1.0 / lam)       # Exponential prende la MEDIA

    # mantieniamo la coerenza con il tuo schema arrivalTemp cumulativo
    arrivalTempScaling += inter
    return arrivalTempScaling
    

    
def percentile_nearest_rank(values, p):
    if not values:
        return 0
    v = sorted(values)
    k = math.ceil((p / 100.0) * len(v)) - 1
    k = max(0, min(k, len(v) - 1))
    return v[k]



# ============================================================
#  TIME-SERIES (solo per scaling): record + plot
# ============================================================

# def record_scaling_timeseries(stats, lam_now):
#     """
#     Registra 3 serie temporali:
#       - lambda(t)
#       - system_avg_response_time(t) (running mean sui completati A3)
#       - numero server attivi layer1 nel tempo

#     """
#     t = stats.t.current

#     # crea le liste se non esistono
#     if not hasattr(stats, "lambda_times"):
#         stats.lambda_times = []
#     if not hasattr(stats, "system_resp_times"):
#         stats.system_resp_times = []
#     if not hasattr(stats, "layer1_servers_times"):
#         stats.layer1_servers_times = []

#     # 1) lambda(t)
#     stats.lambda_times.append((t, lam_now))

#     # 2) system_avg_response_time(t) = (AreaA.node + AreaB.node + service_P) / completati(A3)
    
#     comp_A3 = getattr(stats, "index_A3", 0)
#     if comp_A3 > 0:
#         Rsys = (stats.area_A.node + stats.area_B.node + stats.area_P.service) / comp_A3
#     else:
#         Rsys = 0.0
#     stats.system_resp_times.append((t, Rsys))

#     # 3) numero di server attivi nel tempo
#     n_servers = len(getattr(stats, "layer1_servers", []))
#     stats.layer1_servers_times.append((t, n_servers))


# def _unzip(series):
#     if not series:
#         return [], []
#     xs, ys = zip(*series)
#     return list(xs), list(ys)


