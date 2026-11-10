"""Run the code cells of notebook/station_analysis.ipynb, as they are, in the current environment.

Prints each cell's output (and warnings), and saves the plot to images/monthly-pandas-<version>.png.
If a cell fails, prints the error; with --fix-month, retries the plot with "ME" (the pandas 3 spelling).
Used to capture the 2024 and 2026 outputs shown on the page:

    <2024 env>/bin/python scripts/run_notebook.py
    <2026 env>/bin/python scripts/run_notebook.py --fix-month
"""
import json, os, sys, traceback, warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

here = Path(__file__).resolve().parent.parent
os.chdir(here / "notebook")
cells = [c["source"] for c in json.loads(Path("station_analysis.ipynb").read_text())["cells"] if c["cell_type"] == "code"]
png = here / "images" / f"monthly-pandas-{pd.__version__}.png"
png.parent.mkdir(exist_ok=True)
plt.show = lambda: (plt.gcf().set_size_inches(7, 3.2), plt.tight_layout(), plt.savefig(png, dpi=150), print(f"[saved {png.name}]"))
print(f"Python {sys.version.split()[0]}, pandas {pd.__version__}")
ns = {}
for i, src in enumerate(cells, 1):
    print(f"\n--- cell {i} ---")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            exec(src, ns)
        except Exception as e:
            print("".join(traceback.format_exception_only(e)).strip())
            if "--fix-month" in sys.argv and '"M"' in src:
                print('--- retrying with "ME" ---')
                exec(src.replace('"M"', '"ME"'), ns)
        for x in w:
            if "pandas" in x.filename or x.filename == "<string>":
                print(f"{x.category.__name__}: {str(x.message).splitlines()[0]}")
