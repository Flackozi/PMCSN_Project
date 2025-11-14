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
        if current_checkpoint < len(time_checkpoints) and stats.t.current >= time_checkpoints[current_checkpoint]:
            # snapshot
            comp_A = stats.index_A1 + stats.index_A2 + stats.index_A3  # tutti i depart da A
            comp_B = stats.index_B
            comp_P = stats.index_P

            # medie di attesa e di permanenza (cumulative fino al checkpoint)
            A_wait = (stats.area_A.node - stats.area_A.service) / comp_A if comp_A > 0 else 0.0
            B_wait = (stats.area_B.node - stats.area_B.service) / comp_B if comp_B > 0 else 0.0
            # a P non c'è coda (è delay/think): il "tempo a P" coincide col servizio medio effettivo
            # P_serv = (stats.area_P.service / comp_P) if comp_P > 0 else 0.0
            
            # tempo di risposta del centro = area.node / completamenti
            A_resp = (stats.area_A.node / comp_A) if comp_A > 0 else 0.0
            B_resp = (stats.area_B.node / comp_B) if comp_B > 0 else 0.0

            A1_wait = (stats.area_A1.node - stats.area_A1.service) / stats.index_A1 if stats.index_A1 > 0 else 0.0
            A2_wait = (stats.area_A2.node - stats.area_A2.service) / stats.index_A2 if stats.index_A2 > 0 else 0.0
            A3_wait = (stats.area_A3.node - stats.area_A3.service) / stats.index_A3 if stats.index_A3 > 0 else 0.0
            
            A1_resp = (stats.area_A1.node / stats.index_A1) if stats.index_A1 > 0 else 0.0
            A2_resp = (stats.area_A2.node / stats.index_A2) if stats.index_A2 > 0 else 0.0
            A3_resp = (stats.area_A3.node / stats.index_A3) if stats.index_A3 > 0 else 0.0

            stats.A_wait_times.append((stats.t.current, A_wait))
            stats.B_wait_times.append((stats.t.current, B_wait))
            stats.A1_wait_times.append((stats.t.current, A1_wait))
            stats.A2_wait_times.append((stats.t.current, A2_wait))
            stats.A3_wait_times.append((stats.t.current, A3_wait))

            stats.A_resp_times.append((stats.t.current, A_resp))
            stats.B_resp_times.append((stats.t.current, B_resp))
            stats.A1_resp_times.append((stats.t.current, A1_resp))
            stats.A2_resp_times.append((stats.t.current, A2_resp))
            stats.A3_resp_times.append((stats.t.current, A3_resp))


            # --- istantanee di utilizzo e numero medio fino a ora (transiente cumulato) ---
            # horizon = max(stats.t.current, 1e-12)
            # A_util = stats.area_A.service / horizon
            # B_util = stats.area_B.service / horizon
            # A_N    = stats.area_A.node    / horizon
            # B_N    = stats.area_B.node    / horizon

            # # --- salva punti (t, valore) ---
            # tchk = stats.t.current
            # stats.A_wait_times.append((tchk, A_wait))
            # stats.B_wait_times.append((tchk, B_wait))
            # stats.P_service_times.append((tchk, P_serv))

            # stats.A_sys_times.append((tchk, A_sys))
            # stats.B_sys_times.append((tchk, B_sys))

            # stats.A_util_times.append((tchk, A_util))
            # stats.B_util_times.append((tchk, B_util))
            # stats.A_N_times.append((tchk, A_N))
            # stats.B_N_times.append((tchk, B_N))

            current_checkpoint += 1
            
    stats.calculate_area_queue()  

    # horizon = stats.t.current (last time)
    return return_stats(stats, stats.t.current, s), stats

def update_completion(jobs, current_time):
    if not jobs:
        return INFINITY
    else:
        min_remaining = min(job["remaining"] for job in jobs.values())
        n = len(jobs)
        return current_time + min_remaining * n

def execute(stats, stop):
    if return_times_P:
        stats.t.completion_P = min(return_times_P) #prendo l'elemento che ha il tempo di ritorno in A più piccolo
    else: 
        stats.t.return_P = INFINITY

    stats.t.next = min(stats.t.arrival, stats.t.completion_A, stats.t.completion_B, stats.t.completion_P) #prendo il tempo del prossimo evento    
    dt = stats.t.next - stats.t.current #tempo che ho a disposizione fino al prossimo evento

    if stats.A_jobs:
        nA = len(stats.A_jobs)
        stats.area_A.node += dt * nA #aggiorno area sotto la curva
        stats.area_A.service += dt

        #Per il calcolo delle statistiche per le singole classi in A
        kA1 = sum(1 for j in stats.A_jobs.values() if j["classe"] == 1)
        kA2 = sum(1 for j in stats.A_jobs.values() if j["classe"] == 2)
        kA3 = nA - kA1 - kA2  # più veloce

        # aree per classe in A: node = dt * #job_classe; service = dt * quota_classe
        stats.area_A1.node += dt * kA1
        stats.area_A2.node += dt * kA2
        stats.area_A3.node += dt * kA3

        stats.area_A1.service += dt * (kA1 / nA)
        stats.area_A2.service += dt * (kA2 / nA)
        stats.area_A3.service += dt * (kA3 / nA)

        delta = dt / nA # quanto di tempo che ogni job ha a disposizione (tempo a disposizione / numero di job)
        for job in stats.A_jobs.value():
            job["rem"] -= delta

    if stats.B_jobs :
        nB = len(stats.B_jobs)
        stats.area_B.node += dt * nB
        stats.area_B.service += dt
        delta = dt / nB
        for job in stats.B_jobs.value():
            job["rem"] -= delta

    stats.t.current = stats.t.next #avanziamo l'orologio

    if stats.t.current == stats.t.arrival: 
        #arrivo esterno in A
        jid = stats.next_job_id
        stats.next_job_id += 1
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
            jid = stats.next_job_id 
            stats.next_job_id += 1
            stats.B_jobs[jid] = {"rem": get_service_B()} #aggiungo il job a B
            stats.index_A1 += 1 
            stats.t.completion_B = update_completion(stats.B_jobs, stats.t.current) # aggiorniamo il prossimo completamento di A
        elif job["classe"] == 2:
            #job di classe 2, va in P
            service_P = get_service_P()
            return_time = stats.t.current + service_P #calcolo il tempo di ritorno in A
            return_times_P.append(return_time) #aggiungo il tempo di ritorno in A alla lista
            stats.index_A2 += 1
            stats.area_P.service += service_P #aggiorno l'area di P (tempo di servizio cumulativo)
            
            
        elif job["classe"] == 3:
             #job di classe 3, esce dal sistema
             stats.index_A3 += 1
        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current) # aggiorniamo il prossimo completamento di A
    
    elif stats.t.current == stats.t.completion_B: #completamento in B

        jid, job = min(stats.B_jobs.items(), key=lambda x: x[1]["rem"]) #prendo il job con il tempo di servizio rimanente più piccolo
        del stats.B_jobs[jid] #rimuovo il job da B
        
        stats.index_B += 1
        jid = stats.next_job_id  
        stats.next_job_id += 1
        stats.A_jobs[jid] = {"classe": 2, "rem": get_service_A(2)} #aggiungo il job a A

        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current) # aggiorniamo il prossimo completamento di A
        stats.t.completion_B = update_completion(stats.B_jobs, stats.t.current) # aggiorniamo il prossimo completamento di B

    elif stats.t.current == stats.t.completion_P: #completamento in P

        return_times_P.remove(stats.t.current)
        stats.index_P += 1
        jid = stats.next_job_id  
        stats.next_job_id  += 1
        stats.A_jobs[jid] = {"classe": 3, "rem": get_service_A(3)} #aggiungo il job a A
        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current) # aggiorniamo il prossimo completamento di A

        
def return_stats(stats, horizon, s):
    """Ritorna le statistiche finali della simulazione"""
    # medie finali
    comp_A = stats.index_A1 + stats.index_A2 + stats.index_A3  # tutti i depart da A
    comp_B = stats.index_B
    

    system_avg_response = (stats.area_A.node + stats.area_B.node + stats.area_P.service) / stats.index_A3 if stats.index_A3 > 0 else 0.0
    system_avg_service = (stats.area_A.service + stats.area_B.service + stats.area_P.service) / stats.index_A3 if stats.index_A3 > 0 else 0.0
    system_avg_wait = system_avg_response - system_avg_service

    return {
        "seed": s,

        # statistiche centro A
        "A_avg_resp": stats.area_A.node / comp_A if comp_A > 0 else 0.0,
        "A_avg_wait": stats.area_A.queue / comp_A if comp_A > 0 else 0.0,
        "A_utilization": stats.area_A.service / horizon if horizon > 0 else 0.0,
        "A_avg_num_job": stats.area_A.node / horizon if horizon > 0 else 0.0,
        "A_avg_serv": stats.area_A.service / comp_A if comp_A > 0 else 0.0,

        # statistiche centro B
        "B_avg_resp": stats.area_B.node / comp_B if comp_B > 0 else 0.0,
        "B_avg_wait": stats.area_B.queue / comp_B if comp_B > 0 else 0.0,
        "B_avg_serv": stats.area_B.service / comp_B if comp_B > 0 else 0.0,
        "B_utilization": stats.area_B.service / horizon if horizon > 0 else 0.0,
        "B_avg_num_job": stats.area_B.node / horizon if horizon > 0 else 0.0,   

        # statistiche job di classe 1 su A
        "A1_avg_resp": stats.area_A1.node / stats.index_A1 if stats.index_A1 > 0 else 0.0,
        "A1_avg_wait": stats.area_A1.queue / stats.index_A1 if stats.index_A1 > 0 else 0.0,
        "A1_avg_serv": stats.area_A1.service / stats.index_A1 if stats.index_A1 > 0 else 0.0,
        
        # statistiche job di classe 2 su A
        "A2_avg_resp": stats.area_A2.node / stats.index_A2 if stats.index_A2 > 0 else 0.0,
        "A2_avg_wait": stats.area_A2.queue / stats.index_A2 if stats.index_A2 > 0 else 0.0,
        "A2_avg_serv": stats.area_A2.service / stats.index_A2 if stats.index_A2 > 0 else 0.0,

        # statistiche job di classe 3 su A
        "A3_avg_resp": stats.area_A3.node / stats.index_A3 if stats.index_A3 > 0 else 0.0,
        "A3_avg_wait": stats.area_A3.queue / stats.index_A3 if stats.index_A3 > 0 else 0.0,
        "A3_avg_serv": stats.area_A3.service / stats.index_A3 if stats.index_A3 > 0 else 0.0,

        # ---- METRICHE DI SISTEMA (A3, ingresso→uscita) ----
        'total_completed': stats.indesx_A3,
        'system_avg_response_time': system_avg_response,
        'system_avg_service_time': system_avg_service,
        'system_utilization': (stats.area_A.service + stats.area_B.service + stats.area_P.service) / horizon if horizon > 0 else 0.0,
        'system_avg_wait': system_avg_wait,

        "job_arrived": stats.job_arrived,
        "completions_A1": stats.index_A1,
        "completions_A2": stats.index_A2,
        "completions_A3": stats.index_A3,
        "completions_B": stats.index_B,
        "completions_P": stats.index_P,
        "horizon": horizon

        

    }