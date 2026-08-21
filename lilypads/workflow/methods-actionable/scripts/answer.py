### Solution to the "Actionable Methods" workflow exercise.
# 1. Niño 3.4
# 2. No detrending
# 3. Linear interpolation, monthly step
# 4. Standardize
# 5. MTM, default NW = 4
# 6. Significance testing: 100 Monte Carlo simulations
###
from pathlib import Path
from multiprocessing import freeze_support

import pandas as pd
import pyleoclim as pyleo


def main():
    # Paths
    ROOT_DIR = Path(__file__).resolve().parent.parent
    DATA_FILE = ROOT_DIR / "data" / "nino34.csv"
    FIGURE_DIR = ROOT_DIR / "images"
    FIGURE_DIR.mkdir(exist_ok=True)

    FIGURE_FILE = FIGURE_DIR / "figure1.png"

    # Load Niño 3.4 data
    df = pd.read_csv(DATA_FILE, parse_dates=["date"])

    # Convert monthly dates to fractional years
    time = df["date"].dt.year + (df["date"].dt.month - 1) / 12
    value = df["value"].to_numpy()

    # Create Pyleoclim Series
    ts = pyleo.Series(
        time=time.to_numpy(),
        value=value,
        time_name="Year",
        time_unit="year",
        value_name="Niño Index",
        value_unit="°C",
        label="Niño Index",
    )

    # Linear interpolation onto a regular monthly grid
    ts_interp = ts.interp(
        method="linear",
        step=1 / 12,
    )

    # Multitaper spectral analysis
    psd = ts_interp.standardize().spectral(method="mtm")

    # Significance
    psd_sig = psd.signif_test(number=100)

    # Plot Figure 1
    fig, ax = psd_sig.plot(
        title="Spectral Power of ENSO Variability",
        xlim=[0.5, 20],
    )
    ax.invert_xaxis()

    fig.savefig(
        FIGURE_FILE,
        dpi=300,
        bbox_inches="tight",
    )

    print(f"Saved Figure 1 to {FIGURE_FILE}")


if __name__ == "__main__":
    freeze_support()
    main()