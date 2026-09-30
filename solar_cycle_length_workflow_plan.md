# Workflow Plan: Solar Cycle Length vs. NH Temperature — A Correlation Methodology Case Study

**Addresses:** [LinkedEarth/ThePond#13](https://github.com/LinkedEarth/ThePond/issues/13) — "Correlation-based workflow"
**A LilyPad for [The Pond](https://linked.earth/ThePond/)** (LinkedEarth's open/reproducible-science
learning platform, Quarto-based, `LinkedEarth/ThePond` repo) — self-contained module,
not a standalone package. Intended as a companion tab next to the existing
spectral-analysis LilyPad.

## 1. Purpose

A small, self-contained module that reproduces the core of the Friis-Christensen &
Lassen (1991) solar-cycle-length (SCL) / Northern Hemisphere (NH) land temperature
correlation, and exposes the methodological decisions that turned out to matter in the
ensuing controversy as explicit, user-facing choices — directly implementing the
feature set requested in issue #13 (detrending, regridding, correlation method,
null/UQ model, number of surrogates), instantiated on this one historical case study
rather than a generic multi-series tool for now.

## 2. Step zero for Claude Code — resolve before implementing anything else

**Inspect the existing spectral-analysis LilyPad's source in this repo first.** It
answers two open questions that determine the rest of this plan:

1. **Is it a live interactive widget (e.g. Shinylive-python, pyodide/JupyterLite) or
   statically pre-rendered Quarto output?** This determines whether every
   detrending × method × null × nsim combination needs to be pre-computed at build
   time (static case — keep the option grid small) or whether only the
   learner's selected combination is ever computed on demand (live case — the
   issue's full option set below is cheap regardless of grid size). Match whichever
   pattern the spectral-analysis tab already uses; don't introduce a second
   interactivity model into the same site.
2. **File format/location convention** — `.qmd` vs `.ipynb`, and where in
   `lilypads/` (a `workflow/` or `software/` subfolder) it lives — so this LilyPad
   sits consistently alongside it.

Everything below assumes these get resolved from that existing code, per Julien.

## 3. Locked decisions

- **Period bound**: data restricted to 1850–present (best reliability; also the
  cleanest, most-cited part of the historical dispute). Within that bound, **time
  period is a user-facing choice** (full record vs. a subset, e.g. pre/post-1980) —
  this is explicitly requested in issue #13 and is also the cleanest way to let a
  learner reproduce the original "striking" match on the pre-1980 subset and watch it
  weaken on the full record.
- **Scope**: SCL vs. NH temperature only, as the shipped example. No
  Svensmark/cosmic-ray/cloud-cover companion in this pass. The underlying
  abstractions (Section 5) should stay generic enough that other series (issue #13
  mentions ENSO/NAO indices as the general case) could be plugged in later without a
  rewrite — but only the SCL/temperature pair ships now.
- **No package**: no `pyproject.toml`, no `src/` layout, no installable API surface.
  One module file + one narrative notebook/`.qmd`, matching whatever convention
  Step 0 turns up.

## 4. Option set (matches issue #13 exactly — do not simplify further without checking back)

| Axis | Options | Notes |
|---|---|---|
| Detrending | none, linear | keep to 2; nothing in #13 asks for more |
| Regridding | one default method (e.g. linear interpolation onto a common annual/monthly grid) | required, not a multi-option axis — SCL's native cadence (one value per ~11-year cycle) and monthly NH temperature need aligning |
| Correlation method | **Pearson, Kendall's tau, Spearman's rho** | per #13 — restores Kendall |
| Null model | **AR(1) red noise, phase randomization** | per #13 — replaces the white-noise/red-noise pair from an earlier draft of this plan |
| n_resamples (nsim) | **20, 50, 200, 1000** (discrete, user-selectable) | per #13 exactly — deliberately bounded rather than an open integer, while still letting the learner watch significance flip as nsim increases |
| Time period | full record vs. a learner-chosen subset | per #13 |
| Series | SCL, NH temperature (fixed pair for this pass) | architecture generic; content locked per Section 3 |

If Step 0 finds the existing tab is statically rendered, revisit whether the full
cartesian product above (2 detrend × 3 method × 2 null × 4 nsim × N period choices) is
cheap enough to pre-build, or whether period/nsim need to become live-selected even in
an otherwise static page.

## 5. Data sources

| Series | Source | Coverage | Access |
|---|---|---|---|
| Monthly sunspot number | SILSO, WDC-SILSO, Royal Observatory of Belgium | 1749–present | https://www.sidc.be/SILSO/datafiles |
| NH land temperature anomalies | CRUTEM5, CRU (UEA) + Met Office Hadley Centre | 1850–present, monthly | https://crudata.uea.ac.uk/cru/data/temperature/ |

Restrict both to 1850 onward per Section 3.

## 6. Module design (small, OOP, no package)

```python
# sketch only

class TimeSeries:
    """Immutable (time, value) pair; no analysis logic."""

class SCLTreatment(Protocol):
    def derive(self, sunspots: TimeSeries) -> TimeSeries: ...

class OriginalTreatment(SCLTreatment): ...   # 1-2-2-2-1, inconsistent endpoints (1991 as published)
class CorrectedTreatment(SCLTreatment): ...  # 1-2-1, consistent endpoints (Laut 2003)

class Regridder(Protocol):
    def align(self, a: TimeSeries, b: TimeSeries) -> tuple[TimeSeries, TimeSeries]: ...

class Detrender(Protocol):
    def detrend(self, series: TimeSeries) -> TimeSeries: ...

class NoDetrend(Detrender): ...
class LinearDetrend(Detrender): ...

class CorrelationMetric(Protocol):
    def compute(self, x: TimeSeries, y: TimeSeries) -> float: ...

class PearsonR(CorrelationMetric): ...
class SpearmanRho(CorrelationMetric): ...
class KendallTau(CorrelationMetric): ...

class NullModel(Protocol):
    def p_value(self, x: TimeSeries, y: TimeSeries, metric: CorrelationMetric,
                observed: float, n_resamples: int) -> float: ...

class RedNoiseNull(NullModel): ...          # AR(1)-fitted surrogates
class PhaseRandomizationNull(NullModel): ...

class Experiment:
    """One (scl_treatment, detrender, metric, null_model, n_resamples, period) run."""
    def run(self) -> ExperimentResult: ...
```

## 7. Background (for the narrative notebook, not re-derivation)

- Friis-Christensen, E. & Lassen, K. (1991). *Length of the solar cycle: an indicator
  of solar activity closely associated with climate.* Science 254, 698–700.
  (657 Crossref / 667 Web of Science / ~890 Semantic Scholar citations.)
- Laut, P. (2003). *Solar activity and terrestrial climate: an analysis of some
  purported correlations.* J. Atmos. Solar-Terr. Phys. 65, 801–812. — identifies
  inconsistent 1-2-2-2-1 vs. 1-2-1 filtering/endpoint truncation as the source of the
  apparent post-1980 agreement.
- Damon, P.E. & Laut, P. (2004). *Pattern of strange errors plagues solar activity and
  terrestrial climate data.* Eos 85, 370–374.
- Lassen, K. (1999) — a co-author's own reanalysis concluding SCL no longer tracked NH
  temperature after ~1990.

## 8. Milestones for Claude Code

1. Do Section 2 first — inspect the existing spectral-analysis LilyPad code, confirm
   interactivity model and file conventions.
2. Fetch/cache the two data sources (Section 5).
3. Implement `OriginalTreatment` and `CorrectedTreatment` for SCL derivation; check
   that they diverge only in the last 1–2 cycles, matching the historical account.
4. Implement the regridder, two detrenders, three metrics, two null models
   (`n_resamples` required, drawn from the four values in Section 4).
5. Wire up the full option set from Section 4, in whatever interactivity model
   Step 0 dictated.
6. Highlight two specific configurations explicitly: original treatment on the
   pre-1980 subset (should show the "striking" match) vs. corrected treatment on the
   full record (should show it weaken) — this is the core teaching moment.
7. Let the learner sweep `n_resamples` at fixed everything-else and observe where the
   significance call changes.
8. Narrative text tying results back to Laut (2003) and Damon & Laut (2004).
9. Lightweight self-checks (e.g. red-noise null recovers ~5% false-positive rate on
   synthetic AR(1) surrogates with no true correlation) rather than full pytest/CI
   scaffolding, given this isn't a package with an external API.

## 9. Open items Claude Code should resolve from repo context, not guess

- Interactivity model and file format (Section 2).
- Exact regridding method used elsewhere in the existing spectral-analysis code, for
  consistency.
- Whether "subset" in the time-period axis should be a free date-range picker or a
  small fixed set of historically meaningful windows (e.g. "1860–1980" vs.
  "1860–2000") — check if the spectral-analysis tab's period control offers a
  precedent to follow.
