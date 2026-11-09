"""Write notebook/station_analysis.ipynb, the notebook "Alex" left in March 2024 (no outputs)."""
import json
from pathlib import Path

def md(text): return {"cell_type": "markdown", "metadata": {}, "source": text.strip("\n")}
def code(text): return {"cell_type": "code", "metadata": {}, "execution_count": None,
                        "outputs": [], "source": text.strip("\n")}

cells = [
    md("""
# Station temperatures, 2019–2023

Alex, March 2024. Daily average temperature at the lab's weather station.
Days when the sensor failed are recorded as -999.
"""),
    code("""
# Load the tools: pandas for tables, matplotlib for plots
import pandas as pd
import matplotlib.pyplot as plt

# Read the data: one row per day
df = pd.read_csv("station_daily.csv", parse_dates=["date"], index_col="date")
df.head()
"""),
    code("""
# Mark the sensor failures (-999) as missing
df["temp_C"][df["temp_C"] == -999] = None
"""),
    code("""
# Summarize: the average temperature, and the number of days below freezing
print("Average temperature (°C):", round(df["temp_C"].mean(), 2))
print("Frost days, 2019–2023:", (df["temp_C"] < 0).sum())
"""),
    code("""
# Average the days of each month ("M"), then plot
monthly = df["temp_C"].resample("M").mean()
monthly.plot(ylabel="Monthly average temperature (°C)", xlabel="")
plt.show()
"""),
]
nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
      "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
for i, c in enumerate(cells):
    c["id"] = f"cell-{i}"
out = Path(__file__).resolve().parent.parent / "notebook" / "station_analysis.ipynb"
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
print(f"Wrote {out}")
