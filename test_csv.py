import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
from utils.data_loader import load_data

df, _ = load_data()
print("Data shape:", df.shape)
print("Columns:", df.columns.tolist())
csv_bytes = df.to_csv(index=False).encode("utf-8")
print("CSV utf-8 bytes length:", len(csv_bytes))
csv_sig_bytes = df.to_csv(index=False).encode("utf-8-sig")
print("CSV utf-8-sig bytes length:", len(csv_sig_bytes))
print("First 300 chars of CSV:\n", df.head(2).to_csv(index=False))
