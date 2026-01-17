import pandas as pd

from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "data"
data_in = DATA_PATH / "raw.csv"
data_out = DATA_PATH / "processed.parquet"

df = pd.read_csv(
    data_in,
    dtype={"name": "string", "age": "int"},
)
df["processed"] = 2026

print(df.head())
print(df.info())

df.to_parquet(data_out)
