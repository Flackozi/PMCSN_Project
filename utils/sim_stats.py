

class Stats:
    def __init__(self):
        self.seed = []
        self.A_num_server = []
        self.B_num_server = []

        #Server A
        self.A_witing_time = []
        self.A_delay = []
        self.A_service_time = []
        self.A_utilization = []
        self.A_number_job = []
        self.A_number_queue_job = []

        #Server B
        self.B_witing_time = []
        self.B_delay = []
        self.B_service_time = []
        self.B_utilization = []
        self.B_number_job = []
        self.B_number_queue_job = []

        #class 1 jobs