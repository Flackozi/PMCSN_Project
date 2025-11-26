import traceback
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

    while (stats.t.arrival < stop) or (stats.A_jobs) or (stats.B_jobs) or (len(return_times_P) > 0):
        execute(stats, stop)
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

def infinite_simulation(stop):

    s = getSeed()
    start_time = 0

    batch_stats = ReplicationStats()
    stats = SimulationStats()
    stats.reset(START) 

    reset_arrival_temp()         # azzera la variabile globale arrivalTemp
    stats.reset(START)           # azzera lo stato della simulazione
    stats.t.arrival = GetArrival()   # primo arrivo esterno FINITO, non +inf

    while len(batch_stats.A_avg_wait) < K:
        
        while stats.job_arrived < B:
            execute(stats, stop)
            

        stop_time = stats.t.current - start_time
        start_time = stats.t.current

        stats.calculate_area_queue()

        _check_areas_finite(stats, "infinite_simulation: dopo calculate_area_queue")


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


        # collect replication statistics
        rep_stats = return_stats(stats, stop_time, s)
        write_file(rep_stats, "base_model_infinite_results.csv")
        append_stats(batch_stats, rep_stats, stats)


        # reset stats for next replication
        stats.reset_infinite()

    if PRINT_PLOT_BATCH == 1:
        plot_batch(batch_stats.system_avg_response_time, "standard", "system")
        plot_batch(batch_stats.A_avg_resp, "standard", "center_A")
        plot_batch(batch_stats.B_avg_resp, "standard", "center_B")
        plot_batch(batch_stats.A1_avg_resp, "standard", "class_1_A")
        plot_batch(batch_stats.A2_avg_resp, "standard", "class_2_A")
        plot_batch(batch_stats.A3_avg_resp, "standard", "class_3_A")

    remove_batch(batch_stats, 25)
    return batch_stats

    
def _check_areas_finite(stats, where):
    if not math.isfinite(getattr(stats.area_A, "node", float("nan"))):
        print(f"[ERROR] area_A.node non finito in: {where}")
        print(f"  t.current={getattr(stats.t,'current',None)}, t.next={getattr(stats.t,'next',None)}, dt={(getattr(stats.t,'next',0)-getattr(stats.t,'current',0))}")
        print(f"  arrival={stats.t.arrival}, compA={stats.t.completion_A}, compB={stats.t.completion_B}, compP={stats.t.completion_P}")
        print(f"  return_times_P={return_times_P}")
        print(f"  nA={len(stats.A_jobs)}, A_jobs keys={list(stats.A_jobs.keys())}")
        print(f"  area_A before/after: node={getattr(stats.area_A,'node',None)}, service={getattr(stats.area_A,'service',None)}")
        traceback.print_stack()
        raise RuntimeError("area_A.node non finito")

def infinite_prova(stop):

    """Simulazione infinita di prova, senza l'utilizzo del batch means. 
        Serve a calcolare la serie di tempi di risposta da utilizzare per la scelta del batch size.
    """
    n_completions = 100000 #numero di completamenti da raggiungere
    global current_checkpoint
    current_checkpoint = 0
    s = getSeed()
    reset_arrival_temp()

    stats = SimulationStats()
    stats.reset(vs.START)

    # schedule first external arrival
    stats.t.arrival = GetArrival()

    job_resp_times = []

    while stats.index_A3 < n_completions:
        execute2(stats, stop)

    print("1")

    for job in stats.job_times.values():
        if job["departure"] is not None:
            resp_time = job["departure"] - job["arrival"]
            job_resp_times.append(resp_time)

    print("2")
            
    # scrivo la lista in un file di output acs_raw_rt.dat
    # scrivo la lista in un file di output acs_raw_rt.dat dentro la cartella "output"
    import os
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(project_root, "output")
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "acs_raw_rt.dat")
    with open(out_path, "w") as f:
        for rt in job_resp_times:
            f.write(f"{rt}\n")
    # ...existing code...

    print("3")

    return job_resp_times

def update_completion(jobs, current_time):
    if not jobs:
        return INFINITY
    else:
        min_remaining = min(job["rem"] for job in jobs.values())
        
        # *** AGGIUNGI QUESTO CONTROLLO ***
        if min_remaining < 0:
            print(f"[WARNING] min_remaining negativo: {min_remaining}")
            print(f"  Jobs: {jobs}")
            min_remaining = 0  # Forza a 0 per evitare tempi nel passato
        
        n = len(jobs)
        return current_time + min_remaining * n

def execute(stats, stop):
    if return_times_P:
        stats.t.completion_P = min(return_times_P) #prendo l'elemento che ha il tempo di ritorno in A più piccolo
    else: 
        stats.t.completion_P = INFINITY
        stats.t.return_P = INFINITY

    stats.t.next = min(stats.t.arrival, stats.t.completion_A, stats.t.completion_B, stats.t.completion_P) #prendo il tempo del prossimo evento    
    
    dt = stats.t.next - stats.t.current #tempo che ho a disposizione fino al prossimo evento

    if len(stats.A_jobs)>0:
        nA = len(stats.A_jobs)
        stats.area_A.node += dt * nA #aggiorno area sotto la curva
        stats.area_A.service += dt

        # _check_areas_finite(stats, "execute: dopo aggiornamento area A")

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
        for job in stats.A_jobs.values():
            job["rem"] -= delta

    if stats.B_jobs :
        nB = len(stats.B_jobs)
        stats.area_B.node += dt * nB
        stats.area_B.service += dt
        delta = dt / nB
        for job in stats.B_jobs.values():
            job["rem"] -= delta

    stats.t.current = stats.t.next #avanziamo l'orologio

    if stats.t.current == stats.t.arrival: 
        print(f"ARRIVAL | current: {stats.t.current:.4f}")
        #arrivo esterno in A
        jid = stats.next_job_id
        stats.next_job_id += 1

        stats.A_jobs[jid] =  {"classe": 1, "rem": get_service_A(1)} #aggiungo il job di classe 1 ad A

        stats.job_times[jid] = {"arrival": stats.t.current, "departure": None}  # salvo il tempo di arrivo del job
        

        stats.t.arrival = GetArrival()
        if stats.t.arrival > stop:
            stats.t.last = stats.t.current
            stats.t.arrival = INFINITY
        
        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current) # aggiorniamo il prossimo completamento di A
        stats.job_arrived += 1 #incrementiamo il contatore dei job arrivati

    elif stats.t.current == stats.t.completion_A: #completamento in A
        print(f"COMPLETION_A | current: {stats.t.current:.4f}")
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
            # stats.job_times[jid]["departure"] = stats.t.current

        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current) # aggiorniamo il prossimo completamento di A
    
    elif stats.t.current == stats.t.completion_B: #completamento in B
        print(f"COMPLETION_B | current: {stats.t.current:.4f}")
        jid, job = min(stats.B_jobs.items(), key=lambda x: x[1]["rem"]) #prendo il job con il tempo di servizio rimanente più piccolo
        del stats.B_jobs[jid] #rimuovo il job da B
        
        stats.index_B += 1
        jid = stats.next_job_id  
        stats.next_job_id += 1
        stats.A_jobs[jid] = {"classe": 2, "rem": get_service_A(2)} #aggiungo il job a A

        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current) # aggiorniamo il prossimo completamento di A
        stats.t.completion_B = update_completion(stats.B_jobs, stats.t.current) # aggiorniamo il prossimo completamento di B

    elif stats.t.current == stats.t.completion_P: #completamento in P
        print(f"COMPLETION_P | current: {stats.t.current:.4f}")
        # if return_times_P:
        return_times_P.remove(stats.t.current) #rimuovo il tempo di ritorno in A dalla lista
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
        'total_completed': stats.index_A3,
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




def execute2(stats, stop):
    if return_times_P:
        tp, gid = min(return_times_P)
        stats.t.completion_P = tp #prendo l'elemento che ha il tempo di ritorno in A più piccolo
    else: 
        stats.t.completion_P = INFINITY
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
        for job in stats.A_jobs.values():
            job["rem"] -= delta

    if stats.B_jobs :
        nB = len(stats.B_jobs)
        stats.area_B.node += dt * nB
        stats.area_B.service += dt
        delta = dt / nB
        for job in stats.B_jobs.values():
            job["rem"] -= delta

    stats.t.current = stats.t.next #avanziamo l'orologio

    if stats.t.current == stats.t.arrival: 
        print(f"ARRIVAL | current: {stats.t.current:.4f}")
        #arrivo esterno in A
        jid = stats.next_job_id
        stats.next_job_id += 1

        gid = stats.next_global_id
        stats.next_global_id += 1


        stats.A_jobs[jid] =  {"classe": 1, "rem": get_service_A(1), "gid" : gid} #aggiungo il job di classe 1 ad A

        stats.job_times[gid] = {"arrival": stats.t.current, "departure": None}  # salvo il tempo di arrivo del job
        

        stats.t.arrival = GetArrival()
        # if stats.t.arrival > stop:
        #     stats.t.last = stats.t.current
        #     stats.t.arrival = INFINITY
        
        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current) # aggiorniamo il prossimo completamento di A
        stats.job_arrived += 1 #incrementiamo il contatore dei job arrivati

    elif stats.t.current == stats.t.completion_A: #completamento in A
        print(f"COMPLETION_A | current: {stats.t.current:.4f}")
        jid, job = min(stats.A_jobs.items(), key=lambda x: x[1]["rem"]) #prendo il job con il tempo di servizio rimanente più piccolo
        del stats.A_jobs[jid] #rimuovo il job da A

        if job["classe"] == 1:
            #job di classe 1, va in B
            jid = stats.next_job_id 
            stats.next_job_id += 1

            gid = job["gid"]  # prendo il global id del job che sta andando in B

            stats.B_jobs[jid] = {"rem": get_service_B(), "gid" : gid} #aggiungo il job a B
            stats.index_A1 += 1 
            stats.t.completion_B = update_completion(stats.B_jobs, stats.t.current) # aggiorniamo il prossimo completamento di A
        elif job["classe"] == 2:
            #job di classe 2, va in P
            service_P = get_service_P()
            return_time = stats.t.current + service_P #calcolo il tempo di ritorno in A

            gid = job["gid"]  # prendo il global id del job che sta andando in P
            return_times_P.append((return_time, gid)) #aggiungo il tempo di ritorno in A alla lista
            stats.index_A2 += 1
            stats.area_P.service += service_P #aggiorno l'area di P (tempo di servizio cumulativo)
            
            
        elif job["classe"] == 3:
            #job di classe 3, esce dal sistema
            stats.index_A3 += 1
            gid = job["gid"]  # prendo il global id del job che sta uscendo dal sistema
            stats.job_times[gid]["departure"] = stats.t.current

        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current) # aggiorniamo il prossimo completamento di A
    
    elif stats.t.current == stats.t.completion_B: #completamento in B
        print(f"COMPLETION_B | current: {stats.t.current:.4f}")
        jid, job = min(stats.B_jobs.items(), key=lambda x: x[1]["rem"]) #prendo il job con il tempo di servizio rimanente più piccolo
        del stats.B_jobs[jid] #rimuovo il job da B
        
        stats.index_B += 1
        jid = stats.next_job_id  
        stats.next_job_id += 1

        gid = job["gid"]  # prendo il global id del job che sta tornando in A

        stats.A_jobs[jid] = {"classe": 2, "rem": get_service_A(2), "gid" : gid} #aggiungo il job a A

        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current) # aggiorniamo il prossimo completamento di A
        stats.t.completion_B = update_completion(stats.B_jobs, stats.t.current) # aggiorniamo il prossimo completamento di B

    elif stats.t.current == stats.t.completion_P: #completamento in P
        print(f"COMPLETION_P | current: {stats.t.current:.4f}")
        # rimuovo l'elemento con valore stats.t.current da return_times_P
        tP, gid = min(return_times_P)
        return_times_P.remove((tP, gid))

        
        stats.index_P += 1
        jid = stats.next_job_id  
        stats.next_job_id  += 1
        stats.A_jobs[jid] = {"classe": 3, "rem": get_service_A(3), "gid" : gid} #aggiungo il job a A

        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current) # aggiorniamo il prossimo completamento di A
