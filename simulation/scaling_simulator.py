import utils.variables as vs
import traceback
from utils.sim_utils import*
from utils.sim_output import *
from libraries.rngs import *
from utils.sim_stats import*
from utils.variables import *
import math
from libraries.rngs import *

plantSeeds(SEED)

time_checkpoints = list(range(0, STOP_ANALYSIS, 1000))  # Checkpoint each 1000 sec
current_checkpoint = 0

return_times_P = [] #lista che contiene i tempi dei job che escono da P, e vanno in A


def update_completion(jobs, current_time):
    if not jobs:
        return INFINITY
    else:
        min_remaining = min(job["rem"] for job in jobs.values())
        
        if min_remaining < 0:
            print(f"[WARNING] min_remaining negativo: {min_remaining}")
            print(f"  Jobs: {jobs}")
            min_remaining = 0  # Forza a 0 per evitare tempi nel passato
        
        n = len(jobs)
        return current_time + min_remaining * n
    
# =========================
# funzione per il caso multiserver in B
# =========================
def update_completion_B(jobs, current_time, m_servers: int):
    """
    Completion time per B come PS con m server (pooled).
    - Se n <= m: ogni job usa 1 server -> delta = dt, completion = current + min_rem
    - Se n > m: capacità totale m divisa tra n job -> completion = current + min_rem * n / m
    """
    if not jobs:
        return INFINITY

    n = len(jobs)
    m = max(1, int(m_servers))
    busy = min(m, n)  # server effettivamente occupati

    min_remaining = min(job["rem"] for job in jobs.values())
    if min_remaining < 0:
        min_remaining = 0.0

    return current_time + (min_remaining * n) / busy

 
def adjust_servers_layer1(stats, lambda_current):
    """Aggiunge o rimuove server nel layer 1 in base a λ corrente e ai parametri RHO_UP/RHO_DOWN."""
    stats.layer1_servers

    # se non ci sono server accesi, accendiamo il primo
    if not stats.layer1_servers:
        stats.layer1_servers.append({"id": 0, "jobs": {}})
        return

    num = len(stats.layer1_servers)
    mu = BASE_MU_LAYER1      # tasso di servizio per UN server del layer 1

    if num <= 0:
        return

    rho = lambda_current / (num * mu)

    # scala in su
    if rho > RHO_UP and num < MAX_SERVERS:
        new_id = max(s["id"] for s in stats.layer1_servers) + 1
        stats.layer1_servers.append({"id": new_id, "jobs": {}})
        print(f"[SCALING L1] +1 server, tot={len(stats.layer1_servers)}")

    # scala in giù
    elif rho < RHO_DOWN and num > MIN_SERVERS:
    # nel modello pooled, non usiamo più s["jobs"]
    # rimuovo un server solo se ci sono meno job che server
        if len(stats.B_jobs) < num:
            stats.layer1_servers.pop()
            print(f"[SCALING L1] -1 server, tot={len(stats.layer1_servers)}")



def execute(stats, stop):
    global return_times_P

    # --- COMPLETION IN P ---
    if return_times_P:
        stats.t.completion_P = min(return_times_P)  # prossimo ritorno da P ad A
    else:
        stats.t.completion_P = INFINITY
        stats.t.return_P = INFINITY

    # --- PROSSIMO EVENTO (incluso SPIKE) ---
    stats.t.next = min(
        stats.t.arrival,
        stats.t.completion_A,
        stats.t.completion_B,
        stats.t.completion_P,
        stats.t.completion_spike,   
    )

    dt = stats.t.next - stats.t.current  # tempo fino al prossimo evento

    # --- A: aggiornamento aree e servizio (PS) ---
    if stats.A_jobs:
        nA = len(stats.A_jobs)
        stats.area_A.node += dt * nA
        stats.area_A.service += dt

        kA1 = sum(1 for j in stats.A_jobs.values() if j["classe"] == 1)
        kA2 = sum(1 for j in stats.A_jobs.values() if j["classe"] == 2)
        kA3 = nA - kA1 - kA2

        stats.area_A1.node += dt * kA1
        stats.area_A2.node += dt * kA2
        stats.area_A3.node += dt * kA3

        stats.area_A1.service += dt * (kA1 / nA)
        stats.area_A2.service += dt * (kA2 / nA)
        stats.area_A3.service += dt * (kA3 / nA)

        delta = dt / nA
        for job in stats.A_jobs.values():
            job["rem"] -= delta

    mB = len(stats.layer1_servers) if stats.layer1_servers else 1 # numero di server attivi nel layer 1
    # --- B: aggiornamento aree e servizio (PS) ---
    if stats.B_jobs:
        nB = len(stats.B_jobs) # numero di job in B
        busy = min(mB, nB)

        stats.area_B.node += dt * nB
        stats.area_B.service += dt * busy   # NOTA: ora è "server-seconds" (può essere > dt)

        # quota di servizio ricevuta da ciascun job in dt
        delta = dt * busy / nB
        for job in stats.B_jobs.values():
            job["rem"] -= delta

    # --- SPIKE: aggiornamento aree e servizio (PS) ---
    if stats.spike_server:
        nS = len(stats.spike_server) # numero di job nello spike server
        stats.area_spike.node += dt * nS
        stats.area_spike.service += dt
        delta = dt / nS
        for job in stats.spike_server.values():
            job["rem"] -= delta

    # AVANZA L'OROLOGIO
    stats.t.current = stats.t.next

    # =========================
    #       EVENTI
    # =========================

    # --- ARRIVO ESTERNO IN A ---
    if stats.t.current == stats.t.arrival:
        print(f"ARRIVAL | current: {stats.t.current:.4f}")

        

        jid = stats.next_job_id
        stats.next_job_id += 1

        stats.A_jobs[jid] = {"classe": 1, "rem": get_service_A(1)}

        stats.job_times[jid] = {"arrival": stats.t.current, "departure": None}
        stats.job_arrived += 1

        stats.t.arrival = GetArrivalScaling(stats.t.current)
        if stats.t.arrival > stop:
            stats.t.last = stats.t.current
            stats.t.arrival = INFINITY

        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current)

    # --- COMPLETION IN A ---
    elif stats.t.current == stats.t.completion_A:
        print(f"COMPLETION_A | current: {stats.t.current:.4f}")

        jid, job = min(stats.A_jobs.items(), key=lambda x: x[1]["rem"])
        del stats.A_jobs[jid]

        if job["classe"] == 1:
            # job classe 1 → B oppure SPIKE in base a SI
            # SI = numero di job nel layer 1 (qui usiamo B come layer1 aggregato)

            # SCALING ORIZZONTALE: aggiorno il numero di server del layer 1
            # SCALING ORIZZONTALE: usa lambda variabile
            lam_now = lambda_scaling(stats.t.current)
            adjust_servers_layer1(stats, lambda_current=lam_now)

            # (opzionale) salva lambda per i plot
            if not hasattr(stats, "lambda_times"):
                stats.lambda_times = []
            stats.lambda_times.append((stats.t.current, lam_now))

            SI = len(stats.B_jobs)
            stats.SI_samples.append(SI)


            SI = len(stats.B_jobs)

            if SI < SImax:
                # layer 1 NON saturo → va in B
                jid_B = stats.next_job_id
                stats.next_job_id += 1
                stats.B_jobs[jid_B] = {"rem": get_service_B()}
                stats.index_A1 += 1
                stats.t.completion_B = update_completion_B(stats.B_jobs, stats.t.current, mB)
            else:
                # layer 1 saturo → va allo SPIKE
                jid_S = stats.next_job_id
                stats.next_job_id += 1
                stats.spike_server[jid_S] = {"rem": get_service_spike()}
                stats.index_A1 += 1
                stats.index_spike += 1
                stats.t.completion_spike = update_completion(
                    stats.spike_server, stats.t.current
                )

        elif job["classe"] == 2:
            # job classe 2 → P
            service_P = get_service_P()
            return_time = stats.t.current + service_P
            return_times_P.append(return_time)
            stats.index_A2 += 1
            stats.area_P.service += service_P

        elif job["classe"] == 3:
            # job classe 3 → esce
            stats.index_A3 += 1

        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current)

    # --- COMPLETION IN B ---
    elif stats.t.current == stats.t.completion_B:
        print(f"COMPLETION_B | current: {stats.t.current:.4f}")

        jid, job = min(stats.B_jobs.items(), key=lambda x: x[1]["rem"])
        del stats.B_jobs[jid]

        stats.index_B += 1

        # dopo B → A come classe 2
        jid_A2 = stats.next_job_id
        stats.next_job_id += 1
        stats.A_jobs[jid_A2] = {"classe": 2, "rem": get_service_A(2)}

        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current)
        stats.t.completion_B = update_completion_B(stats.B_jobs, stats.t.current, mB)

    # --- COMPLETION IN P ---
    elif stats.t.current == stats.t.completion_P:
        print(f"COMPLETION_P | current: {stats.t.current:.4f}")

        return_times_P.remove(stats.t.current)
        stats.index_P += 1

        jid = stats.next_job_id
        stats.next_job_id += 1
        stats.A_jobs[jid] = {"classe": 3, "rem": get_service_A(3)}

        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current)

    # --- COMPLETION NELLO SPIKE ---
    elif stats.t.current == stats.t.completion_spike:
        print(f"COMPLETION_SPIKE | current: {stats.t.current:.4f}")

        jid, job = min(stats.spike_server.items(), key=lambda x: x[1]["rem"])
        del stats.spike_server[jid]

        # lo tratto come B "potenziato" → dopo spike → A come classe 2
        jid_A2 = stats.next_job_id
        stats.next_job_id += 1
        stats.A_jobs[jid_A2] = {"classe": 2, "rem": get_service_A(2)}

        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current)
        stats.t.completion_spike = update_completion(stats.spike_server, stats.t.current)

# =========================
#   SIMULAZIONE FINITA
# =========================

def scaling_finite_simulation(stop):
    """
    Simulazione FINITA con scaling dinamico,
    strutturata come finite_simulation(stop) del modello base.
    """
    global current_checkpoint, return_times_P
    current_checkpoint = 0
    return_times_P = []

    s = getSeed()
    reset_arrival_temp_scaling()

    stats = SimulationStats()
    stats.reset(vs.START)

    # opzionale: almeno un server nel layer 1
    stats.layer1_servers = [{"id": 0, "jobs": {}}]

    # primo arrivo esterno
    stats.t.arrival = GetArrivalScaling(stats.t.current)

    while (
    (stats.t.arrival < stop)
    or stats.A_jobs
    or stats.B_jobs
    or stats.spike_server
    or (return_times_P and min(return_times_P) < INFINITY)
    ):
        execute(stats, stop)

        # snapshot come nel modello base
        if current_checkpoint < len(time_checkpoints) and stats.t.current >= time_checkpoints[current_checkpoint]:
            comp_A = stats.index_A1 + stats.index_A2 + stats.index_A3
            comp_B = stats.index_B
            comp_P = stats.index_P

            A_wait = (stats.area_A.node - stats.area_A.service) / comp_A if comp_A > 0 else 0.0
            B_wait = (stats.area_B.node - stats.area_B.service) / comp_B if comp_B > 0 else 0.0

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

            lam_now = lambda_scaling(stats.t.current)

            if not hasattr(stats, "lambda_times"):
                stats.lambda_times = []
            stats.lambda_times.append((stats.t.current, lam_now))

            if not hasattr(stats, "layer1_servers_times"):
                stats.layer1_servers_times = []
            stats.layer1_servers_times.append((stats.t.current, len(stats.layer1_servers)))

            if not hasattr(stats, "system_resp_times"):
                stats.system_resp_times = []
            comp_A3 = stats.index_A3
            Rsys = (stats.area_A.node + stats.area_B.node + stats.area_P.service) / comp_A3 if comp_A3 > 0 else 0.0
            stats.system_resp_times.append((stats.t.current, Rsys))

            current_checkpoint += 1

    stats.calculate_area_queue()
    horizon = stats.t.current

    si_p99 = percentile_nearest_rank(stats.SI_samples, 99)
    SImax_est = si_p99 + 1   
    print("SImax stimato (p99+1) =", SImax_est)


    return return_stats(stats, horizon, s), stats



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
