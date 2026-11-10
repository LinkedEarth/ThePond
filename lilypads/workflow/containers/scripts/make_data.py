"""Create station_daily.csv: five years of fictional daily temperatures.

Two days, when the sensor failed, are recorded as -999.
Run once; the CSV is committed. Requires numpy and pandas (any version).
"""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(49)  # issue #49
dates = pd.date_range("2019-01-01", "2023-12-31", freq="D")
day = dates.dayofyear.to_numpy()
seasonal = 11.5 - 9.5 * np.cos(2 * np.pi * (day - 15) / 365.25)
noise = np.zeros(len(dates))
for i in range(1, len(dates)):  # weather persists from one day to the next
    noise[i] = 0.7 * noise[i - 1] + rng.normal(0, 2.4)
temp = np.round(seasonal + noise, 1)

df = pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "temp_C": temp})
for d in ["2020-02-11", "2022-07-19"]:  # sensor failures
    df.loc[df["date"] == d, "temp_C"] = -999

out = Path(__file__).resolve().parent.parent / "notebook" / "station_daily.csv"
df.to_csv(out, index=False)
print(f"Wrote {out}")
