from utils.sim_utils import*
from utils.sim_output import *
from libraries.rngs import *
from utils.sim_stats import*
from utils.variables import *


plantSeeds(SEED)

time_checkpoints = list(range(0, STOP_ANALYSIS, 1000))  # Checkpoint each 1000 sec
current_checkpoint = 0

return_times_P = [] #lista che contiene i tempi dei job che escono da P, e vanno in A

def finite_simulation(stop):
    global current_checkpoint
    current_checkpoint = 0
    s = getSeed()
    reset_arrival_temp()

    stats = SimulationStats()
    stats.reset(vs.START)

    # schedule first external arrival
    stats.t.arrival = GetArrival()

    while (stats.t.arrival < STOP) or (stats.A_jobs > 0) or (stats.B_jobs) or (len(return_times_P) > 0):
        execute(stats, STOP)
    

    stats.calculate_area_queue()
    # horizon = stats.t.current (last time)
    return return_stats(stats, stats.t.current), stats

def execute(stats, stop):
    
    next_job_id = 0

    if return_times_P:
        stats.t.completion_P = min(return_times_P)
    else: 
        stats.t.return_P = INFINITY

    stats.t.next = min(stats.t.arrival, stats.t.completion_A, stats.t.completion_B, stats.t.completion_P)    
    dt = stats.t.next - stats.t.current #tempo che ho a disposizione fino al prossimo evento

    if stats.A_jobs:
        nA = len(stats.A_jobs)
        stats.area_A += dt * nA
        delta = dt / nA
        for job in stats.A_jobs.value():
            job["rem"] -= delta

    if stats.B_jobs :
        nB = len(stats.B_jobs)
        stats.area_B += dt * nB
        delta = dt / nB
        for job in stats.B_jobs.value():
            job["rem"] -= delta

    stats.t.current = stats.t.next #avanziamo l'orologio

    if stats.t.current == stats.t.arrival: 
        #arrivo esterno in A
        jid = next_job_id
        next_job_id += 1
        stats.A_jobs[jid] =  {"classe": 1, "rem": get_service_A()}

        stats.t.arrival = GetArrival()
        if stats.t.arrival > STOP:
            stats.t,last = stats.t.current
            stats.t.arrival = INFINITY
        
        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current)
