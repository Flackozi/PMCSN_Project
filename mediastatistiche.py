import pandas as pd

FILE = "output/csv/scaling_model_finite_results.csv"

df = pd.read_csv(FILE)

# Rimuove spazi prima/dopo nei nomi delle colonne
df.columns = df.columns.str.strip()

centers = {
    "A": [
        "A_avg_resp",
        "A_avg_wait",
        "A_avg_serv",
        "A_utilization",
        "A_avg_num_job",
    ],
    "B": [
        "B_avg_resp",
        "B_avg_wait",
        "B_avg_serv",
        "B_utilization",
        "B_avg_num_job",
    ],
    "P": [
        "P_avg_resp",
        "P_avg_wait",
        "P_avg_serv",
        "P_utilization",
        "P_avg_num_job",
    ],
    "SYSTEM": [
        "system_avg_response_time",
        "system_avg_wait",
        "system_avg_service_time",
        "system_utilization",
    ]
}

print("\n=== MEDIE DELLE METRICHE ===\n")

for center, cols in centers.items():
    print(f"--- Centro {center} ---")
    for col in cols:
        mean_value = df[col].mean()
        print(f"{col}: {mean_value:.6f}")
    print()
