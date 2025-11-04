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

def update_completion(jobs, current_time):
    if not jobs:
        return INFINITY
    else:
        min_remaining = min(job["remaining"] for job in jobs.values())
        n = len(jobs)
        return current_time + min_remaining * n

def execute(stats, stop):
    
    next_job_id = 0 # il next_job_id è un contatore globale per assegnare un id diverso ad ogni job

    if return_times_P:
        stats.t.completion_P = min(return_times_P) #prendo l'elemento che ha il tempo di ritorno in A più piccolo
    else: 
        stats.t.return_P = INFINITY

    stats.t.next = min(stats.t.arrival, stats.t.completion_A, stats.t.completion_B, stats.t.completion_P) #prendo il tempo del prossimo evento    
    dt = stats.t.next - stats.t.current #tempo che ho a disposizione fino al prossimo evento

    if stats.A_jobs:
        nA = len(stats.A_jobs)
        stats.area_A += dt * nA #aggiorno area sotto la curva
        delta = dt / nA # quanto di tempo che ogni job ha a disposizione (tempo a disposizione / numero di job)
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
        stats.A_jobs[jid] =  {"classe": 1, "rem": get_service_A(1)} #aggiungo il job di classe 1 ad A

        stats.t.arrival = GetArrival()
        if stats.t.arrival > STOP:
            stats.t.last = stats.t.current
            stats.t.arrival = INFINITY
        
        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current) # aggiorniamo il prossimo completamento di A
        stats.job_arrived += 1 #incrementiamo il contatore dei job arrivati

    elif stats.t.current == stats.t.completion_A: #completamento in A

        jid, job = min(stats.A_jobs.items(), key=lambda x: x[1]["rem"]) #prendo il job con il tempo di servizio rimanente più piccolo
        del stats.A_jobs[jid] #rimuovo il job da A

        if job["classe"] == 1:
            #job di classe 1, va in B
            jid = next_job_id 
            next_job_id += 1
            stats.B_jobs[jid] = {"rem": get_service_B()} #aggiungo il job a B
            #stats.index_A1 += 1 incremento il contatore dei job completati in A1
            stats.t.completion_B = update_completion(stats.B_jobs, stats.t.current) # aggiorniamo il prossimo completamento di A
        elif job["classe"] == 2:
            #job di classe 2, va in P
            service_P = get_service_P()
            return_time = stats.t.current + service_P #calcolo il tempo di ritorno in A
            return_times_P.append(return_time) #aggiungo il tempo di ritorno in A alla lista
            #stats.index_A2 += 1
        # elif job["classe"] == 3:
        #     #job di classe 3, esce dal sistema
        #     stats.index_A3 += 1
        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current) # aggiorniamo il prossimo completamento di A
    
    elif stats.t.current == stats.t.completion_B: #completamento in B

        jid, job = min(stats.B_jobs.items(), key=lambda x: x[1]["rem"]) #prendo il job con il tempo di servizio rimanente più piccolo
        del stats.B_jobs[jid] #rimuovo il job da B
        
        jid = next_job_id 
        next_job_id += 1
        stats.A_jobs[jid] = {"classe": 2, "rem": get_service_A(2)} #aggiungo il job a A

        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current) # aggiorniamo il prossimo completamento di A
        stats.t.completion_B = update_completion(stats.B_jobs, stats.t.current) # aggiorniamo il prossimo completamento di B

    elif stats.t.current == stats.t.completion_P: #completamento in P

        return_times_P.remove(stats.t.current)
        jid = next_job_id 
        next_job_id += 1
        stats.A_jobs[jid] = {"classe": 3, "rem": get_service_A(3)} #aggiungo il job a A
        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current) # aggiorniamo il prossimo completamento di A

        
