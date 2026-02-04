class Track:
    # aree integrate nel tempo per calcolare le medie
    def __init__(self):
        self.node = 0.0   # ∫ N(t) dt sull'orizzonte
        self.queue = 0.0  # = node - service (per PS, queue ≈ 0)
        self.service = 0.0  # tempo occupato (un server): incrementa di dt quando N>0
        self.capacity = 0.0   # ∫ m(t) dt (secondi di server attivo)

class Time:
    def __init__(self):
        self.arrival = float('inf')       # prossimo arrivo esterno
        self.completion_A = float('inf')  # prossimo completamento in A (PS min-rem * N) | tempo di completamento più piccolo tra i job in A
        self.completion_B = float('inf')  # prossimo completamento in B (PS)
        self.completion_P = float('inf')  # prossimo completamento in P (centro ritardo)
        self.current = 0.0
        self.next = 0.0
        self.last = 0.0
        self.completion_spike = float('inf')
        self.rho_check = float('inf')   # nuovo evento periodico

# -----------------------------
# SimulationStats (singola esecuzione)
# -----------------------------
class SimulationStats:
    """
    Contiene lo stato dinamico di una singola replica (evento per evento).
    """
    def __init__(self):
        # contatori di arrivi e completamenti
        self.job_arrived = 0      # totale job arrivati al sistema

        self.index_A1 = 0   # completamenti in A durante visita A1
        self.index_A2 = 0
        self.index_A3 = 0
        self.index_B  = 0
        self.index_P  = 0



        # popolazioni (a livello di nodo)
        self.number_A  = 0  # = len(A_jobs)
        self.number_B  = 0  # = len(B_jobs)
        self.number_P  = 0  # P in servizio/in coda (se la coda è modellata)

        # suddivisione delle visite in A (conteggi per split area e reporting)
        self.number_A1 = 0
        self.number_A2 = 0
        self.number_A3 = 0

        # tempi di servizio rimanenti di A
        self.remaining_A = []
        self.remaining_B = []
        self.remainng_P = []

        # liste di job PS con servizio rimanente
        # stage è 'A1'|'A2'|'A3' per A; solo servizio rimanente per B
        self.A_jobs = {} # [{'stage': 'A1'|'A2'|'A3', 'rem': float}, ...]
        self.B_jobs = {} # [{'rem': float}, ...]
        self.P_jobs = {}

    
        # struttura temporale
        self.t = Time()

        # aree (aggregate per nodo)
        self.area_A = Track()
        self.area_B = Track()
        self.area_P = Track()

        # aree per visita in A (decomposizione)
        self.area_A1 = Track()
        self.area_A2 = Track()
        self.area_A3 = Track()

        # serie temporali transitorie opzionali
        self.A_wait_times  = []
        self.B_wait_times  = []
        self.P_wait_times  = []
        self.A1_wait_times = []
        self.A2_wait_times = []
        self.A3_wait_times = []

        self.A_resp_times  = []
        self.B_resp_times  = []
        self.P_resp_times  = []
        self.A1_resp_times = []
        self.A2_resp_times = []
        self.A3_resp_times = []

        # id progressivo dei job (lo usiamo in simulator.py)
        self.next_job_id = 0

        self.next_global_id = 0
        

        self.job_times = {}  # dizionario in cui mi salvo i tempi di arrivo dei job {job_id: arrival_time} e i tempi di uscita {job_id: departure_time}

        # scaling dinamico
        self.layer1_servers = []
        self.spike_server = {}
        self.index_spike = 0
        self.area_spike = Track()
        self.spike_events = []  # timestamp di arrivo dei job nello spike
        self.SI_samples = []

        # --- Serie temporali popolazione (per plot variabilità) ---
        self.NA_times = []      # (t, N_A)
        self.NB_times = []      # (t, N_B)
        self.NP_times = []      # (t, N_P)  = len(stats.P_jobs)
        self.Nsys_times = []    # (t, N_sistema)

        self.raw_rt = []  # lista dei tempi di risposta grezzi (per calcolo IC esterno)
        
    def reset(self, start_time):
        """Resettiamo tutte le variabili per una nuova simulazione"""
        self.t.current = start_time
        self.t.completion_A = float('inf')
        self.t.completion_B = float('inf')
        self.t.completion_P = float('inf')
        
        # stato dei nodi
        self.A_jobs.clear()
        self.B_jobs.clear()
        self.P_jobs.clear()

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

        self.SI_samples.clear()
        # --- autoscaling: misure su finestra per rho_B ---
        self.last_B_service = 0.0
        self.last_B_capacity = 0.0
        self.rhoB_samples = []


    def calculate_area_queue(self):
        """Calcola l'area della coda come differenza tra area nodo e area servizio"""
        self.area_A1.queue = self.area_A1.node - self.area_A1.service
        self.area_A2.queue = self.area_A2.node - self.area_A2.service
        self.area_A3.queue = self.area_A3.node - self.area_A3.service
        self.area_A.queue  = self.area_A.node  - self.area_A.service
        self.area_B.queue  = self.area_B.node  - self.area_B.service
        self.area_P.queue  = self.area_P.node  - self.area_P.service

    def reset_infinite(self):
        """Resettiamo tutte le variabili per una nuova simulazione infinita"""
        self.t.current = 0.0
        self.t.completion_A = float('inf')
        self.t.completion_B = float('inf')
        self.t.completion_P = float('inf')
        
        # stato dei nodi
        self.A_jobs.clear()
        self.B_jobs.clear()
        self.P_jobs.clear()

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

        self.t.rho_check = float('inf')
        self.last_B_service = 0.0
        self.last_B_capacity = 0.0
        self.rhoB_samples.clear()


        
class ReplicationStats:
    """
    Raccoglie tutte le statistiche a livello di replica per il flusso A–B–A–P–A.
    Ogni attributo memorizza una lista contenente il valore di una metrica per
    ogni replica della simulazione (per calcolare successivamente medie e IC).

    Centri:
        A  -> Server Web/Edge (visitato 3 volte: A1, A2, A3)
        B  -> Server Backend / Business Logic
        P  -> Provider di pagamento (esterno, ritardo incontrollabile)
    """

    def __init__(self):
        # --- Informazioni meta ---
        self.seed = []                # Semi RNG usati per replica

        # --- Metriche complessive a livello sistema ---
        self.system_avg_wait = []         # Tempo medio di attesa del sistema
        self.system_avg_response_time = []# Tempo medio di risposta del sistema                 
        self.system_avg_service_time = [] # Tempo totale di servizio (somma di tutti i centri)
        self.system_utilization = []      # utilizzo complessivo
        self.system_avg_num_job = []      # Numero medio di job nel sistema
        self.system_throughput = []       # Throughput del sistema

        # --- Nodo A (aggregato su tutte le visite) ---
        self.A_avg_wait = []           # Tempo medio di attesa in A
        self.A_avg_resp = []           # Tempo medio di risposta in A
        self.A_avg_serv = []           # Tempo di servizio in A
        self.A_utilization = []        # Utilizzo di A
        self.A_avg_num_job = []        # Numero medio di job in A
        self.A_throughput = []         # Throughput di A

        # --- Nodo B ---
        self.B_avg_wait = []           # Tempo medio di attesa in B
        self.B_avg_serv = []           # Tempo di servizio in B
        self.B_avg_resp = []           # Tempo medio di risposta in B 
        self.B_utilization = []        # Utilizzo di B
        self.B_avg_num_job = []        # Numero medio di job in B
        self.B_throughput = []         # Throughput di B

        # --- Nodo P (M/M/1 PS) ---
        self.P_avg_wait = []           # Tempo medio di attesa in P
        self.P_avg_serv = []           # Tempo di servizio in P
        self.P_avg_resp = []           # Tempo medio di risposta in P 
        self.P_utilization = []        # Utilizzo di P
        self.P_avg_num_job = []        # Numero medio di job in P
        self.P_throughput = []         # Throughput di P

        self.A1_avg_wait = []          # Tempo medio di attesa in A1
        self.A1_avg_resp = []          # Tempo medio di risposta in A1
        self.A1_avg_serv = []          # Tempo di servizio in A1

        self.A2_avg_wait = []          # Tempo medio di attesa in A2
        self.A2_avg_resp = []          # Tempo medio di risposta in A2
        self.A2_avg_serv = []          # Tempo di servizio in A2

        self.A3_avg_wait = []          # Tempo medio di attesa in A3
        self.A3_avg_resp = []          # Tempo medio di risposta in A3
        self.A3_avg_serv = []          # Tempo di servizio in A3

        # --- Dati di serie temporali (per analisi transitoria) ---
        self.A_wait_interval = []      # Traccia tempo di attesa in A nel tempo
        self.B_wait_interval = []      # Traccia tempo di attesa in B
        self.P_wait_interval = []      # Traccia tempo di attesa in P
        self.A1_wait_interval = []     # Serie temporale per A1
        self.A2_wait_interval = []     # Serie temporale per A2
        self.A3_wait_interval = []     # Serie temporale per A3

        self.A_resp_interval = []      # Traccia tempo di risposta in A nel tempo
        self.B_resp_interval = []      # Traccia tempo di risposta in B
        self.P_resp_interval = []      # Traccia tempo di risposta in P
        self.A1_resp_interval = []     # Serie temporale per A1
        self.A2_resp_interval = []     # Serie temporale per A2
        self.A3_resp_interval = []     # Serie temporale per A3

