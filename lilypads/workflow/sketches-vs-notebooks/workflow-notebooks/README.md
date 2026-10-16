# From workflow sketch to notebook — reference materials

Four Python reference notebooks and matching synthetic CSV datasets for The Pond.
Unzip the complete folder, install requirements with `python -m pip install -r requirements.txt`,
then open JupyterLab from this folder. Keep the data folder next to the notebooks.
Each notebook already contains captured outputs; run all cells from top to bottom to reproduce them.
No network access is needed after installing dependencies. No intermediate dataset is written to disk.

## Contents
- hydrology.ipynb — duplicate averaging, QC, measurement range, station means.
- seismology.ipynb — catalog cleaning, date/magnitude selection, spatial counts.
- oceanography.ipynb — unit conversion, QA, depth selection, binned means.
- geophysics.ipynb — simplified frame conversion, filtering, station trends and velocities.
- data/*.csv — synthetic inputs; field meanings are in each notebook.
- build_materials.py — deterministic generator (seed 24092026), which recreates data and notebooks.

## Suggested learner exercise
Use one scenario. Provide the working code and figures, then blank selected Markdown
input/parameter/output descriptions. Learners fill these in by tracing their sketch,
then explain which later cell consumes one intermediate output. Start with one fully
annotated step. Ask learners to predict the effect of changing a parameter before rerunning.
Their edited notebook is their individual response. These delivered notebooks are complete
reference versions, not the blank learner versions.

## Decisions to review before teaching
Hydrology: all duplicate members must pass QC for their mean to pass; dates have equal weight.
Seismology: an approximate local projection is used, with fixed grid origin and extent.
Oceanography: keep QA=0 only, including exclusion of unchecked rows; pool measurements across profiles.
Geophysics: fictional frame offsets, elapsed-span record length, unweighted linear fits.
These choices fill gaps in the sketches and should be made explicit to learners.
All data are fictional; plots illustrate methods, not empirical scientific claims.
