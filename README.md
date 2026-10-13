# Card & Krueger Minimum-Wage Replication

**Student:** Shang Fangfei  
**Student ID:** 3036763658

## Project overview

This project replicates Tables 2-4 and Figure 1 in Card and Krueger (1994),
*Minimum Wages and Employment: A Case Study of the Fast-Food Industry in New
Jersey and Pennsylvania*. It also conducts an independent ownership
heterogeneity analysis. Table 1 is outside the assigned replication scope.

The research question is whether New Jersey's April 1992 minimum-wage increase
reduced fast-food employment relative to eastern Pennsylvania. The replication
reconstructs full-time-equivalent (FTE) employment from the original restaurant
survey, reports the paper's descriptive comparisons and reduced-form models, and
compares estimates with the published results.

## Project layout

```text
README.md
report.pdf
AI_USE_DISCLOSURE.md
data/
  raw/                 Course-provided Package 01 input and documentation
  processed/           Derived store-level analysis data (not for public upload)
code/
  run_all.py           One-command entry point
  others/
    replicate.py       Data preparation, estimates, tables, figure, and report
outputs/
  tables/              Generated CSV tables
  figures/             Generated figures
skills/
  SKILL.md             Reusable instructions for regenerating and checking outputs
requirements.txt
```

`report/empirical_report.md` is retained as the editable source used to generate
the submitted `report.pdf`.

## Input data and access

Obtain the course-approved **Package 01 (01_DID)** and place its `public.csv` at:

```text
data/raw/public.csv
```

The package's `README.md` and `DATA_DICTIONARY.md` are retained in `data/raw/`.
Keep the course-provided CSV name and contents unchanged. The raw restaurant
survey and row-level derived data are excluded from Git because the course
restricts redistribution. Do not upload them to a public repository. The
teaching team should access the inputs through the course-approved source.

## Reproduce all outputs

Use Python 3.10 or later. From the project root, install the listed dependencies
and run the single entry point:

```powershell
python -m pip install -r requirements.txt
python code/run_all.py
```

The entry point validates the input schema and record counts, creates the
processed data under `data/processed/`, generates the tables and figure under
`outputs/`, and rebuilds both the editable report source and `report.pdf`.
No manual edits to the data or analysis code are needed.

## Empirical definitions

- FTE employment is `EMPFT + NMGRS + 0.5 * EMPPT`.
- Employment at the six permanently closed restaurants (`STATUS2 == 3`) is zero
  in wave 2. Temporary closures (`STATUS2` 2, 4, or 5) are missing in the main
  comparisons and set to zero only in Table 3 row 5.
- The Table 4 wage gap is zero in Pennsylvania and for New Jersey restaurants
  with an initial wage at or above $5.05. Otherwise it is
  `($5.05 - wave-1 starting wage) / wave-1 starting wage`.
- The Table 4 sample includes 357 restaurants with employment in both waves and
  an initial wage. Wave-2 wage is required for open/responding restaurants;
  permanently closed restaurants are retained with wave-2 employment set to 0.
- New Jersey wage groups in Table 3 are $4.25, $4.26-$4.99, and $5.00 or more;
  their full-sample counts are 101, 140, and 73.
- In Table 3 row 3, the level-change estimate uses all available responses in
  each wave. Its standard error is based on paired within-store changes for
  stores observed in both waves. Row 4 uses the balanced sample for both the
  estimate and standard error.
- The independent extension tests whether the NJ-by-post employment effect
  differs for company-owned versus franchise-owned stores, with store fixed
  effects and standard errors clustered by store.

## Git and submission

Git tracks the analysis, documentation, tables, and figures in meaningful
stages. `data/raw/public.csv` and `data/processed/*.csv` are deliberately ignored
to prevent accidental publication of store-level data. Review `AI_USE_DISCLOSURE.md`
and the limitations in `report.pdf` before submission. The course submission
requires an accessible GitHub repository URL; this local project must be pushed
to the student's own approved GitHub repository before sharing that URL.
