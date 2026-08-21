### This code fetches the El Nino data from the NOAA website and saves it as a CSV file.

from pathlib import Path
from io import StringIO

import pandas as pd
import requests


DATASETS = {
    "nino3.csv": "https://psl.noaa.gov/data/correlation/nina3.anom.csv",
    "nino34.csv": "https://psl.noaa.gov/data/correlation/nina34.anom.csv",
    "nino4.csv": "https://psl.noaa.gov/data/correlation/nina4.anom.csv",
}

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Dates deliberately removed to create short gaps in the time series.
# The same dates are removed from all three ENSO indices.
MISSING_DATES = [
    "1962-04-01",
    "1962-05-01",
    "1971-09-01",
    "1980-02-01",
    "1980-03-01",
    "1980-04-01",
    "1987-11-01",
    "1995-06-01",
    "1995-07-01",
    "2003-03-01",
    "2010-08-01",
    "2010-09-01",
]


for filename, url in DATASETS.items():
    print(f"Downloading {filename}...")

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text))

    # Standardize column names
    df.columns = ["date", "value"]

    # Parse dates and remove NOAA missing values
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df[df["value"] != -9999].dropna()

    # Introduce identical artificial gaps into each series
    missing_dates = pd.to_datetime(MISSING_DATES)
    df = df[~df["date"].isin(missing_dates)]

    df.to_csv(DATA_DIR / filename, index=False)

    print(f"Saved {filename}: {len(df)} observations")

print("Done!")