# Card & Krueger Minimum-Wage Replication

This project reproduces Card and Krueger (1994), *Minimum Wages and Employment:
A Case Study of the Fast-Food Industry in New Jersey and Pennsylvania*, for
Tables 2-4 and Figure 1. It also includes an independent ownership-heterogeneity
extension.

## Input data

The analysis uses the course-provided Package 01 file:

```text
01_DID/data/public.csv
```

Keep the course-provided folder and CSV names unchanged. The source package's
README and data dictionary are in `01_DID/`. Raw survey data and row-level
processed data are excluded from Git because the assignment treats the source
data as restricted. Do not upload either file to a public repository. A reviewer
must obtain the package through the course-approved channel and place it at the
documented path.

## Reproduce the tables and figure

Use Python 3.10 or later. From this project directory:

```powershell
python -m pip install -r requirements.txt
python src/replicate.py
```

The script validates required columns, 410 input records, the 357-store Table 4
sample, and the main Table 4 estimates. It then writes:

```text
output/
  processed_data.csv
  figures/figure1_wage_distribution.png
  tables/table2_summary.csv
  tables/table3_employment.csv
  tables/table4_regressions.csv
  tables/ownership_heterogeneity.csv
  tables/ownership_group_means.csv
report/empirical_report.md
```

No manual editing of input data or analysis code is needed to regenerate the
outputs. The original paper PDF is a user-provided reference and is not included
in this repository.

## Variable construction and sample rules

- FTE employment is `EMPFT + NMGRS + 0.5 * EMPPT`.
- Table 2's full-time-employment share is `EMPFT / FTE`, matching the source
  table's definition.
- Wave-2 employment at the six permanently closed restaurants (`STATUS2 == 3`)
  is zero. Temporary closures (`STATUS2` 2, 4, or 5) are missing in the main
  analysis and set to zero only for Table 3's final sensitivity comparison.
- The Table 4 wage-gap measure is zero for Pennsylvania and for New Jersey
  stores at or above $5.05. Otherwise it is
  `($5.05 - wave-1 starting wage) / wave-1 starting wage`.
- Table 4 includes stores with usable employment in both waves and a wave-1
  starting wage. Wave-2 wage is required for open/responding stores; permanently
  closed stores remain in the sample even though their wave-2 wage is missing.
  This yields the paper's 357-store sample.
- Table 3 splits New Jersey stores by wave-1 starting wage: exactly $4.25,
  $4.26-$4.99, and $5.00 or more.
- The extension estimates store and wave fixed effects and tests whether the
  NJ-by-post employment effect differs for company-owned restaurants. Standard
  errors are clustered by store.

## Git and AI-use disclosure

Use Git to track meaningful stages such as data checks, core replication,
extension, and report review. Do not commit `01_DID/data/public.csv` or
`output/processed_data.csv`. See the empirical report for the AI-use disclosure
and replication limitations.
