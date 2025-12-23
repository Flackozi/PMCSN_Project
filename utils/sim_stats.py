class Track:
    # time-integrated areas for averages
    def __init__(self):
        self.node = 0.0   # ∫ N(t) dt over the horizon
        self.queue = 0.0  # = node - service (for PS, queue ≈ 0)
        self.service = 0.0  # busy time (one server): increments by dt when N>0

class Time:
    def __init__(self):
        self.arrival = float('inf')       # next external arrival time
        self.completion_A = float('inf')  # next completion at A (PS min-rem * N) | tempo di completamento più piccolo tra i job in A
        self.completion_B = float('inf')  # next completion at B (PS)
        self.completion_P = float('inf')  # next completion at P (delay center)
        self.current = 0.0
        self.next = 0.0
        self.last = 0.0
        self.completion_spike = float('inf')

# -----------------------------
# SimulationStats (single run)
# -----------------------------
class SimulationStats:
    """
    Holds the dynamic state of a single replication (event-by-event).
    This is PS-ready for A and B (jobs list with remaining service).
    P is modeled as a delay center with single-service completion.
    """
    def __init__(self):
        # arrivals & completions counters
        self.job_arrived = 0      # total jobs arrived to the system

        self.index_A1 = 0   # completions at A while in visit A1
        self.index_A2 = 0
        self.index_A3 = 0
        self.index_B  = 0
        self.index_P  = 0


        # populations (node-level)
        self.number_A  = 0  # = len(A_jobs)
        self.number_B  = 0  # = len(B_jobs)
        #self.number_P  = 0  # P in service/queued (if queue modeled)

        # visits split at A (counts for area split and reporting)
        self.number_A1 = 0
        self.number_A2 = 0
        self.number_A3 = 0

        #tempi di servizio rimamenti di A
        self.remaining_A = []
        self.remaining_B = []

        # PS job lists with remaining service
        # stage is 'A1'|'A2'|'A3' for A; only remaining for B
        self.A_jobs = {} # [{'stage': 'A1'|'A2'|'A3', 'rem': float}, ...]
        self.B_jobs = {} # [{'rem': float}, ...]

        # we keep a simple scalar for P (delay center)
        # if you want an explicit queue for P, add self.P_jobs list
        # and manage multiple completions; otherwise keep single completion time.
        
        # time structure
        self.t = Time()

        # areas (aggregate per node)
        self.area_A = Track()
        self.area_B = Track()
        self.area_P = Track()

        # areas per visit for A (decomposition)
        self.area_A1 = Track()
        self.area_A2 = Track()
        self.area_A3 = Track()

        # optional transient time series
        self.A_wait_times  = []
        self.B_wait_times  = []
        self.A1_wait_times = []
        self.A2_wait_times = []
        self.A3_wait_times = []

        self.A_resp_times  = []
        self.B_resp_times  = []
        self.A1_resp_times = []
        self.A2_resp_times = []
        self.A3_resp_times = []

        # id progressivo dei job (lo usiamo in simulator.py)
        self.next_job_id = 0

        self.next_global_id = 0
        

        self.job_times = {}  # dizionario in cui mi salvo i tempi di arrivo dei job {job_id: arrival_time} e i tempi di uscita {job_id: departure_time}

        #scaling dinamico
        self.layer1_servers = []
        self.spike_server = {}
        self.index_spike = 0
        self.area_spike = Track()
        
    def reset(self, start_time):
        """Resettiamo tutte le variabili per una nuova simulazione"""
        self.t.current = start_time
        self.t.completion_A = float('inf')
        self.t.completion_B = float('inf')
        
        #stato dei nodi
        self.A_jobs.clear()
        self.B_jobs.clear()

         # aree
        self.area_A = Track()
        self.area_B = Track()
        self.area_P = Track()
        self.area_A1 = Track()
        self.area_A2 = Track()
        self.area_A3 = Track()

        # --- stato scaling dinamico ---
        self.layer1_servers.clear()
        self.spike_server.clear()
        self.index_spike = 0
        self.area_spike = Track()
        self.t.completion_spike = float('inf')

        # contatori base
        self.job_arrived = 0
        self.index_A1 = self.index_A2 = self.index_A3 = 0
        self.index_B  = 0
        self.index_P  = 0

        self.next_job_id = 0

    def calculate_area_queue(self):
        """Calcola l'area della coda come differenza tra area nodo e area servizio"""
        self.area_A1.queue = self.area_A1.node - self.area_A1.service
        self.area_A2.queue = self.area_A2.node - self.area_A2.service
        self.area_A3.queue = self.area_A3.node - self.area_A3.service
        self.area_A.queue  = self.area_A.node  - self.area_A.service
        self.area_B.queue  = self.area_B.node  - self.area_B.service

    def reset_infinite(self):
        """Resettiamo tutte le variabili per una nuova simulazione infinita"""
        self.t.current = 0.0
        self.t.completion_A = float('inf')
        self.t.completion_B = float('inf')
        
        #stato dei nodi
        self.A_jobs.clear()
        self.B_jobs.clear()

        # --- stato scaling dinamico ---
        self.layer1_servers.clear()
        self.spike_server.clear()
        self.index_spike = 0
        self.area_spike = Track()
        self.t.completion_spike = float('inf')

         # aree
        self.area_A = Track()
        self.area_B = Track()
        self.area_P = Track()

        # contatori base
        self.job_arrived = 0
        self.index_A1 = self.index_A2 = self.index_A3 = 0
        self.index_B  = 0
        self.index_P  = 0

        self.next_job_id = 0


        
class ReplicationStats:
    """
    Collects all replication-level statistics for the A–B–A–P–A workflow.
    Each attribute stores one list containing the value of a metric for
    every replication of the simulation (to later compute means & CIs).

    Centers:
        A  -> Web/Edge server (visited 3 times: A1, A2, A3)
        B  -> Backend / Business Logic server
        P  -> Payment provider (external, uncontrollable delay)
    """

    def __init__(self):
        # --- Meta information ---
        self.seed = []                # RNG seeds used per replication

        # --- System-level overall metrics ---
        self.system_avg_wait = []         # System average waiting time
        self.system_avg_response_time = []# System average response time                 
        self.system_avg_service_time = [] # Total service time (sum of all centers)
        self.system_utilization = []      # (Optional) overall utilization

        # --- Node A (aggregated across all visits) ---
        self.A_avg_wait = []           # Average waiting time at A
        self.A_avg_resp = []           # Average response time at A
        self.A_avg_serv = []           # Service time at A
        self.A_utilization = []        # Utilization of A
        self.A_avg_num_job = []        # Avg number of jobs in A

        # --- Node B ---
        self.B_avg_wait = []           # Average waiting time at B
        self.B_avg_serv = []           # Service time at B
        self.B_avg_resp = []           # Average response time at B 
        self.B_utilization = []        # Utilization of B
        self.B_avg_num_job = []        # Avg number of jobs in B


        self.A1_avg_wait = []          # Average waiting time at A1
        self.A1_avg_resp = []          # Average response time at A1
        self.A1_avg_serv = []          # Service time at A1

        self.A2_avg_wait = []          # Average waiting time at A2
        self.A2_avg_resp = []          # Average response time at A2
        self.A2_avg_serv = []          # Service time at A2

        self.A3_avg_wait = []          # Average waiting time at A3
        self.A3_avg_resp = []          # Average response time at A3
        self.A3_avg_serv = []          # Service time at A3

        # # --- Time-series data (for transient analysis) ---
        self.A_wait_interval = []      # A wait-time trace over time
        self.B_wait_interval = []      # B wait-time trace
        self.A1_wait_interval = []     # Time series for A1
        self.A2_wait_interval = []     # Time series for A2
        self.A3_wait_interval = []     # Time series for A3

        self.A_resp_interval = []       # A response-time trace over time
        self.B_resp_interval = []       # B response-time trace
        self.A1_resp_interval = []     # Time series for A1
        self.A2_resp_interval = []     # Time series for A2
        self.A3_resp_interval = []     # Time series for A3


        # # --- Batch Means (for infinite-run analysis) ---
        # self.A_batch_means = []        # Average wait per batch (A)
        # self.B_batch_means = []
        # self.P_batch_means = []
        # self.sys_batch_means = []

    # # ----------------------------------------------------------------------
    # # You could later add helper methods here, for example:
    # # ----------------------------------------------------------------------

    # def append_replica(self, results, stats):
    #     """
    #     Example method to append a single replica's metrics to the lists.
    #     'results' would come from the simulation output (dict),
    #     and 'stats' from the SimulationStats object.
    #     """
    #     self.A_wait_times.append(results['A_avg_wait'])
    #     self.B_wait_times.append(results['B_avg_wait'])
    #     self.P_delays.append(results['P_avg_delay'])
    #     self.sys_delays.append(results['sys_avg_delay'])
    #     self.seeds.append(results['seed'])

