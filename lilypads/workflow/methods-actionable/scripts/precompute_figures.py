from pathlib import Path
from itertools import product
from multiprocessing import freeze_support
import json

import pandas as pd
import pyleoclim as pyleo


# -----------------------------
# Configuration
# -----------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
OUT_DIR = ROOT_DIR / "images" / "generated"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DATASETS = {
    "nino3": {
        "label": "Niño 3",
        "file": DATA_DIR / "nino3.csv",
    },
    "nino34": {
        "label": "Niño 3.4",
        "file": DATA_DIR / "nino34.csv",
    },
    "nino4": {
        "label": "Niño 4",
        "file": DATA_DIR / "nino4.csv",
    },
}

DETREND_OPTIONS = {
    "none": {"label": "None"},
    "linear": {"label": "Linear"},
    "constant": {"label": "Constant"},
    "savitzky-golay": {"label": "Savitzky-Golay"},
    "emd": {"label": "EMD"},
}

REGRID_OPTIONS = {
    "none": {"label": "None"},
    "linear": {"label": "Linear"},
    "cubic": {"label": "Cubic spline"},
    "bin": {"label": "Binning"},
}

# UI label -> pyleoclim method
SPECTRAL_OPTIONS = {
    "fourier": {"label": "Fourier", "method": "periodogram"},
    "mtm": {"label": "MTM", "method": "mtm"},
    "lomb-scargle": {"label": "Lomb–Scargle", "method": "lomb_scargle"},
}

SIGNIF_OPTIONS = {
    "none": 0,
    "100": 100,
    "250": 250,
    "500": 500,
}


# -----------------------------
# Helpers
# -----------------------------
def load_series(dataset_key):
    meta = DATASETS[dataset_key]
    df = pd.read_csv(meta["file"], parse_dates=["date"])

    time = df["date"].dt.year + (df["date"].dt.month - 1) / 12
    value = df["value"].to_numpy()

    ts = pyleo.Series(
        time=time.to_numpy(),
        value=value,
        time_name="Year",
        time_unit="CE",
        value_name=f"{meta['label']} SST anomaly",
        value_unit="°C",
        label=meta["label"],
    )
    return ts


def apply_detrend(ts, detrend_key):
    if detrend_key == "none":
        return ts
    return ts.detrend(method=detrend_key)


def apply_interp(ts, interp_key):
    if interp_key == "none":
        return ts
    elif interp_key == "bin":
        return ts.bin()
    else:
        return ts.interp(method=interp_key, step=1 / 12)


def valid_spectral_choices(interp_key):
    if interp_key == "none":
        return ["lomb-scargle"]
    return ["fourier", "mtm", "lomb-scargle"]


def make_filename(dataset_key, detrend_key, interp_key, spectral_key, signif_key):
    return (
        f"{dataset_key}"
        f"__detrend-{detrend_key}"
        f"__regrid-{interp_key}"
        f"__spec-{spectral_key}"
        f"__sig-{signif_key}.png"
    )


def generate_figure(dataset_key, detrend_key, interp_key, spectral_key, signif_key):
    filename = make_filename(
        dataset_key, detrend_key, interp_key, spectral_key, signif_key
    )
    out_file = OUT_DIR / filename

    if out_file.exists():
        return filename

    ts = load_series(dataset_key)
    ts = apply_detrend(ts, detrend_key)
    ts = apply_interp(ts, interp_key)

    # Standardize under the hood
    ts = ts.standardize()

    psd = ts.spectral(method=SPECTRAL_OPTIONS[spectral_key]["method"])

    n_mc = SIGNIF_OPTIONS[signif_key]
    if n_mc > 0:
        psd_to_plot = psd.signif_test(number=n_mc)
    else:
        psd_to_plot = psd

    fig, ax = psd_to_plot.plot(
        title="Spectral Power of ENSO Variability",
        xlim=[0.5, 20],
    )
    ax.invert_xaxis()

    fig.savefig(out_file, dpi=300, bbox_inches="tight")
    return filename


# -----------------------------
# Main
# -----------------------------
def main():
    manifest = []
    total = 0

    for dataset_key, detrend_key, interp_key in product(
        DATASETS.keys(),
        DETREND_OPTIONS.keys(),
        REGRID_OPTIONS.keys(),
    ):
        for spectral_key in valid_spectral_choices(interp_key):
            for signif_key in SIGNIF_OPTIONS.keys():
                total += 1
                print(
                    f"[{total}] "
                    f"{dataset_key}, {detrend_key}, {interp_key}, {spectral_key}, sig={signif_key}"
                )

                try:
                    filename = generate_figure(
                        dataset_key,
                        detrend_key,
                        interp_key,
                        spectral_key,
                        signif_key,
                    )

                    manifest.append(
                        {
                            "dataset": dataset_key,
                            "detrend": detrend_key,
                            "regridding": interp_key,
                            "spectral": spectral_key,
                            "significance": signif_key,
                            "image": f"images/generated/{filename}",
                        }
                    )

                except Exception as e:
                    print("FAILED:", e)

    manifest_file = OUT_DIR / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2))
    print(f"\nSaved manifest to {manifest_file}")
    print(f"Generated/registered {len(manifest)} figure entries.")


if __name__ == "__main__":
    freeze_support()
    main()