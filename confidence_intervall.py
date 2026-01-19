import csv
import math
import statistics
from libraries import rvms   # stessa libreria che usi nel progetto

# =========================
# PARAMETRI
# =========================
CSV_FILE = "output/csv/base_model_finite_results.csv"
METRIC = "system_avg_response_time"
ALPHA = 0.05
TARGET_RELATIVE_ERROR = 0.05  # 5%

# =========================
# LETTURA DATI
# =========================
data = []

with open(CSV_FILE, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        value = float(row[METRIC])
        data.append(value)

n = len(data)

if n < 2:
    raise ValueError("Servono almeno 2 repliche")

# =========================
# STATISTICHE
# =========================
mean = statistics.mean(data)
stdev = statistics.stdev(data)

# quantile della distribuzione t di Student
t_star = rvms.idfStudent(n - 1, 1 - ALPHA / 2)

# semi-ampiezza CI
half_width = t_star * stdev / math.sqrt(n)

# errore relativo
relative_error = half_width / mean

# =========================
# STIMA NUOVO NUMERO DI REPLICHE
# =========================
target_half_width = TARGET_RELATIVE_ERROR * mean

required_replications = math.ceil(
    n * (half_width / target_half_width) ** 2
)

# =========================
# OUTPUT
# =========================
print("===== RISULTATI CI =====")
print(f"Repliche attuali          : {n}")
print(f"Media                     : {mean:.6f}")
print(f"Deviazione standard       : {stdev:.6f}")
print(f"t* (Student)              : {t_star:.4f}")
print(f"Semi-ampiezza CI (95%)    : {half_width:.6f}")
print(f"Errore relativo           : {relative_error*100:.2f}%")
print()
print("===== STIMA REPLICHE =====")
print(f"Target errore relativo    : {TARGET_RELATIVE_ERROR*100:.1f}%")
print(f"Repliche consigliate      : {required_replications}")
