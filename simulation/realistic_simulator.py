import traceback
from utils.sim_utils import *
from utils.sim_output import *
from libraries.rngs import *
from utils.sim_stats import *
from utils.variables import *

plantSeeds(SEED)

time_checkpoints = list(range(0, STOP_ANALYSIS, 1000))  # Checkpoint ogni 1000 sec
current_checkpoint = 0


def realistic_finite_simulation(stop):
    """
    Simulazione finita del modello base con arrivi iper-esponenziali
    e tasso di arrivo variabile nel tempo (lambda_scaling).
    """
    global current_checkpoint
    current_checkpoint = 0

    s = getSeed()
    reset_arrival_temp_realistic()

    stats = SimulationStats()
    stats.reset(vs.START)

    # Primo arrivo: iper-esponenziale con lambda variabile
    stats.t.arrival = GetHyperArrivalScaling(stats.t.current)

    while (stats.t.arrival < stop) or (stats.A_jobs) or (stats.B_jobs) or (stats.P_jobs):
        execute(stats, stop)
        if current_checkpoint < len(time_checkpoints) and stats.t.current >= time_checkpoints[current_checkpoint]:
            comp_A = stats.index_A1 + stats.index_A2 + stats.index_A3
            comp_B = stats.index_B
            comp_P = stats.index_P

            A_wait = (stats.area_A.node - stats.area_A.service) / comp_A if comp_A > 0 else 0.0
            B_wait = (stats.area_B.node - stats.area_B.service) / comp_B if comp_B > 0 else 0.0
            P_wait = (stats.area_P.node - stats.area_P.service) / comp_P if comp_P > 0 else 0.0

            A_resp = (stats.area_A.node / comp_A) if comp_A > 0 else 0.0
            B_resp = (stats.area_B.node / comp_B) if comp_B > 0 else 0.0
            P_resp = (stats.area_P.node / comp_P) if comp_P > 0 else 0.0

            A1_wait = (stats.area_A1.node - stats.area_A1.service) / stats.index_A1 if stats.index_A1 > 0 else 0.0
            A2_wait = (stats.area_A2.node - stats.area_A2.service) / stats.index_A2 if stats.index_A2 > 0 else 0.0
            A3_wait = (stats.area_A3.node - stats.area_A3.service) / stats.index_A3 if stats.index_A3 > 0 else 0.0

            A1_resp = (stats.area_A1.node / stats.index_A1) if stats.index_A1 > 0 else 0.0
            A2_resp = (stats.area_A2.node / stats.index_A2) if stats.index_A2 > 0 else 0.0
            A3_resp = (stats.area_A3.node / stats.index_A3) if stats.index_A3 > 0 else 0.0
            system_resp = (stats.area_A.node + stats.area_B.node + stats.area_P.node) / stats.index_A3 if stats.index_A3 > 0 else 0.0

            stats.A_wait_times.append((stats.t.current, A_wait))
            stats.B_wait_times.append((stats.t.current, B_wait))
            stats.P_wait_times.append((stats.t.current, P_wait))
            stats.A1_wait_times.append((stats.t.current, A1_wait))
            stats.A2_wait_times.append((stats.t.current, A2_wait))
            stats.A3_wait_times.append((stats.t.current, A3_wait))

            stats.A_resp_times.append((stats.t.current, A_resp))
            stats.B_resp_times.append((stats.t.current, B_resp))
            stats.P_resp_times.append((stats.t.current, P_resp))
            stats.A1_resp_times.append((stats.t.current, A1_resp))
            stats.A2_resp_times.append((stats.t.current, A2_resp))
            stats.A3_resp_times.append((stats.t.current, A3_resp))
            stats.system_resp_times.append((stats.t.current, system_resp))

            current_checkpoint += 1

    stats.calculate_area_queue()

    return return_stats(stats, stats.t.current, s), stats


def update_completion(jobs, current_time):
    if not jobs:
        return INFINITY
    else:
        min_remaining = min(job["rem"] for job in jobs.values())

        if min_remaining < 0:
            print(f"[WARNING] min_remaining negativo: {min_remaining}")
            min_remaining = 0

        n = len(jobs)
        return current_time + min_remaining * n


def record_num_jobs(stats):
    nA = len(stats.A_jobs)
    nB = len(stats.B_jobs)
    nP = len(stats.P_jobs)
    nSys = nA + nB + nP

    t = stats.t.current
    stats.NA_times.append((t, nA))
    stats.NB_times.append((t, nB))
    stats.NP_times.append((t, nP))
    stats.Nsys_times.append((t, nSys))


def execute(stats, stop):
    stats.t.next = min(stats.t.arrival, stats.t.completion_A, stats.t.completion_B, stats.t.completion_P)

    dt = stats.t.next - stats.t.current

    if len(stats.A_jobs) > 0:
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

    if stats.B_jobs:
        nB = len(stats.B_jobs)
        stats.area_B.node += dt * nB
        stats.area_B.service += dt
        delta = dt / nB
        for job in stats.B_jobs.values():
            job["rem"] -= delta

    if stats.P_jobs:
        nP = len(stats.P_jobs)
        stats.area_P.node += dt * nP
        stats.area_P.service += dt
        delta = dt / nP
        for job in stats.P_jobs.values():
            job["rem"] -= delta

    stats.t.current = stats.t.next

    if stats.t.current == stats.t.arrival:
        jid = stats.next_job_id
        stats.next_job_id += 1

        stats.A_jobs[jid] = {"classe": 1, "rem": get_service_A(1)}
        stats.job_times[jid] = {"arrival": stats.t.current, "departure": None}

        stats.t.arrival = GetHyperArrivalScaling(stats.t.current)
        if stats.t.arrival > stop:
            stats.t.last = stats.t.current
            stats.t.arrival = INFINITY

        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current)
        stats.job_arrived += 1

    elif stats.t.current == stats.t.completion_A:
        jid, job = min(stats.A_jobs.items(), key=lambda x: x[1]["rem"])
        del stats.A_jobs[jid]

        if job["classe"] == 1:
            jid = stats.next_job_id
            stats.next_job_id += 1
            stats.B_jobs[jid] = {"rem": get_service_B()}
            stats.index_A1 += 1
            stats.t.completion_B = update_completion(stats.B_jobs, stats.t.current)
        elif job["classe"] == 2:
            jid_P = stats.next_job_id
            stats.next_job_id += 1
            stats.P_jobs[jid_P] = {"rem": get_service_P()}
            stats.index_A2 += 1
            stats.t.completion_P = update_completion(stats.P_jobs, stats.t.current)
        elif job["classe"] == 3:
            stats.index_A3 += 1

        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current)

    elif stats.t.current == stats.t.completion_B:
        jid, job = min(stats.B_jobs.items(), key=lambda x: x[1]["rem"])
        del stats.B_jobs[jid]

        stats.index_B += 1
        jid = stats.next_job_id
        stats.next_job_id += 1
        stats.A_jobs[jid] = {"classe": 2, "rem": get_service_A(2)}

        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current)
        stats.t.completion_B = update_completion(stats.B_jobs, stats.t.current)

    elif stats.t.current == stats.t.completion_P:
        jid, job = min(stats.P_jobs.items(), key=lambda x: x[1]["rem"])
        del stats.P_jobs[jid]

        stats.index_P += 1
        jid = stats.next_job_id
        stats.next_job_id += 1
        stats.A_jobs[jid] = {"classe": 3, "rem": get_service_A(3)}

        stats.t.completion_A = update_completion(stats.A_jobs, stats.t.current)
        stats.t.completion_P = update_completion(stats.P_jobs, stats.t.current)

    record_num_jobs(stats)


def return_stats(stats, horizon, s):
    comp_A = stats.index_A1 + stats.index_A2 + stats.index_A3
    comp_B = stats.index_B
    comp_P = stats.index_P

    system_avg_response = (stats.area_A.node + stats.area_B.node + stats.area_P.node) / stats.index_A3 if stats.index_A3 > 0 else 0.0
    system_avg_service = (stats.area_A.service + stats.area_B.service + stats.area_P.service) / stats.index_A3 if stats.index_A3 > 0 else 0.0
    system_avg_wait = system_avg_response - system_avg_service

    return {
        "seed": s,

        "A_avg_resp": stats.area_A.node / comp_A if comp_A > 0 else 0.0,
        "A_avg_wait": stats.area_A.queue / comp_A if comp_A > 0 else 0.0,
        "A_utilization": stats.area_A.service / horizon if horizon > 0 else 0.0,
        "A_avg_num_job": stats.area_A.node / horizon if horizon > 0 else 0.0,
        "A_avg_serv": stats.area_A.service / comp_A if comp_A > 0 else 0.0,
        "A_throughput": comp_A / horizon if horizon > 0 else 0.0,

        "B_avg_resp": stats.area_B.node / comp_B if comp_B > 0 else 0.0,
        "B_avg_wait": stats.area_B.queue / comp_B if comp_B > 0 else 0.0,
        "B_avg_serv": stats.area_B.service / comp_B if comp_B > 0 else 0.0,
        "B_utilization": stats.area_B.service / horizon if horizon > 0 else 0.0,
        "B_avg_num_job": stats.area_B.node / horizon if horizon > 0 else 0.0,
        "B_throughput": comp_B / horizon if horizon > 0 else 0.0,

        "P_avg_resp": stats.area_P.node / comp_P if comp_P > 0 else 0.0,
        "P_avg_wait": stats.area_P.queue / comp_P if comp_P > 0 else 0.0,
        "P_avg_serv": stats.area_P.service / comp_P if comp_P > 0 else 0.0,
        "P_utilization": stats.area_P.service / horizon if horizon > 0 else 0.0,
        "P_avg_num_job": stats.area_P.node / horizon if horizon > 0 else 0.0,
        "P_throughput": comp_P / horizon if horizon > 0 else 0.0,

        "A1_avg_resp": stats.area_A1.node / stats.index_A1 if stats.index_A1 > 0 else 0.0,
        "A1_avg_wait": stats.area_A1.queue / stats.index_A1 if stats.index_A1 > 0 else 0.0,
        "A1_avg_serv": stats.area_A1.service / stats.index_A1 if stats.index_A1 > 0 else 0.0,

        "A2_avg_resp": stats.area_A2.node / stats.index_A2 if stats.index_A2 > 0 else 0.0,
        "A2_avg_wait": stats.area_A2.queue / stats.index_A2 if stats.index_A2 > 0 else 0.0,
        "A2_avg_serv": stats.area_A2.service / stats.index_A2 if stats.index_A2 > 0 else 0.0,

        "A3_avg_resp": stats.area_A3.node / stats.index_A3 if stats.index_A3 > 0 else 0.0,
        "A3_avg_wait": stats.area_A3.queue / stats.index_A3 if stats.index_A3 > 0 else 0.0,
        "A3_avg_serv": stats.area_A3.service / stats.index_A3 if stats.index_A3 > 0 else 0.0,

        'total_completed': stats.index_A3,
        'system_avg_response_time': system_avg_response,
        'system_avg_service_time': system_avg_service,
        'system_utilization': (stats.area_A.service + stats.area_B.service + stats.area_P.service) / horizon if horizon > 0 else 0.0,
        'system_avg_num_job': (stats.area_A.node + stats.area_B.node + stats.area_P.node) / horizon if horizon > 0 else 0.0,
        'system_avg_wait': system_avg_wait,
        'system_throughput': stats.index_A3 / horizon if horizon > 0 else 0.0,

        "job_arrived": stats.job_arrived,
        "completions_A1": stats.index_A1,
        "completions_A2": stats.index_A2,
        "completions_A3": stats.index_A3,
        "completions_B": stats.index_B,
        "completions_P": stats.index_P,
        "horizon": horizon
    }
