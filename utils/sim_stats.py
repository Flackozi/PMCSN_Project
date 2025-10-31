class Track:
    # time-integrated areas for averages
    def __init__(self):
        self.node = 0.0   # ∫ N(t) dt over the horizon
        self.queue = 0.0  # = node - service (for PS, queue ≈ 0)
        self.service = 0.0  # busy time (one server): increments by dt when N>0

class Time:
    def __init__(self):
        self.arrival = float('inf')       # next external arrival time
        self.completion_A = float('inf')  # next completion at A (PS min-rem * N)
        self.completion_B = float('inf')  # next completion at B (PS)
        self.completion_P = float('inf')  # next completion at P (delay center)
        self.current = 0.0
        self.next = 0.0
        self.last = 0.0

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
        self.job_arrived = 0

        self.index_A1 = 0   # completions at A while in visit A1
        self.index_A2 = 0
        self.index_A3 = 0
        self.index_B  = 0
        self.index_P  = 0

        # populations (node-level)
        self.number_A  = 0  # = len(A_jobs)
        self.number_B  = 0  # = len(B_jobs)
        self.number_P  = 0  # P in service/queued (if queue modeled)

        # visits split at A (counts for area split and reporting)
        self.number_A1 = 0
        self.number_A2 = 0
        self.number_A3 = 0

        # PS job lists with remaining service
        # stage is 'A1'|'A2'|'A3' for A; only remaining for B
        self.A_jobs = []  # [{'stage': 'A1'|'A2'|'A3', 'rem': float}, ...]
        self.B_jobs = []  # [{'rem': float}, ...]

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
        self.P_wait_times  = []
        self.A1_wait_times = []
        self.A2_wait_times = []
        self.A3_wait_times = []

        
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
        self.seeds = []                # RNG seeds used per replication
        self.A_num_servers = []        # Number of servers in A (if scalable)
        self.B_num_servers = []
        # self.P_num_servers = []        # Usually constant (external)

        # --- System-level overall metrics ---
        self.sys_wait_times = []       # System average waiting time
        self.sys_delays = []           # End-to-end response time
        self.sys_service_times = []    # Total service time (sum of all centers)
        self.sys_number_node = []      # Avg number of jobs in the system
        self.sys_throughput = []       # System throughput
        self.sys_utilization = []      # (Optional) overall utilization

        # --- Node A (aggregated across all visits) ---
        self.A_wait_times = []         # Average waiting time at A
        self.A_delays = []             # Response time at A
        self.A_service_times = []      # Service time at A
        self.A_utilization = []        # Utilization of A
        self.A_number_node = []        # Avg number of jobs in A
        self.A_number_queue = []       # Avg number of waiting jobs in A

        # --- Node B ---
        self.B_wait_times = []         # Average waiting time at B
        self.B_delays = []             # Response time at B
        self.B_service_times = []      # Service time at B
        self.B_utilization = []        # Utilization of B
        self.B_number_node = []        # Avg number of jobs in B
        self.B_number_queue = []       # Avg number of waiting jobs in B

        # --- Node P (external payment provider) ---
        # Only delay metrics are tracked since P is not under our control
        self.P_delays = []             # End-to-end delay at P (service only)
        self.P_service_times = []      # Service times drawn for P
        self.P_wait_times = []         # Optional: same as delay if no queue

        # --- A's three visits (A1, A2, A3) ---
        # A1: initial request (Class 1), A2: after B(Class 2), A3: after P (Class 3)
        self.A1_jobs_leaving = []      # Completed jobs at A1
        self.A1_wait_times = []
        self.A1_delays = []
        self.A1_service_times = []
        self.A1_utilization = []
        self.A1_number_node = []
        self.A1_number_queue = []

        self.A2_jobs_leaving = []      # Completed jobs at A2
        self.A2_wait_times = []
        self.A2_delays = []
        self.A2_service_times = []
        self.A2_utilization = []
        self.A2_number_node = []
        self.A2_number_queue = []

        self.A3_jobs_leaving = []      # Completed jobs at A3
        self.A3_wait_times = []
        self.A3_delays = []
        self.A3_service_times = []
        self.A3_utilization = []
        self.A3_number_node = []
        self.A3_number_queue = []

        # # --- Time-series data (for transient analysis) ---
        # self.A_wait_interval = []      # A wait-time trace over time
        # self.B_wait_interval = []      # B wait-time trace
        # self.P_wait_interval = []      # P delay trace (if needed)
        # self.A1_wait_interval = []     # Time series for A1
        # self.A2_wait_interval = []     # Time series for A2
        # self.A3_wait_interval = []     # Time series for A3
        # self.sys_delay_interval = []   # System response trace (for steady-state)

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
