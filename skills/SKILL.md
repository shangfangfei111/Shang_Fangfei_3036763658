# Skill: Reproduce Card-Krueger Tables and Figure

## Purpose

Regenerate the assigned Card and Krueger (1994) outputs from the course-provided
Package 01 survey data, with consistent sample rules and no hand-edited output.

## Inputs

- `data/raw/public.csv` from course Package 01
- `data/raw/DATA_DICTIONARY.md` and `data/raw/README.md`

Do not rename, modify, or publish the restricted raw data.

## Run

From the project root:

```powershell
python code/run_all.py
```

The workflow generates processed data under `data/processed/`, CSV tables under
`outputs/tables/`, Figure 1 under `outputs/figures/`, and a PDF report at the
project root.

## Required checks

1. Confirm that the input has 410 records and all required columns.
2. Confirm that the New Jersey starting-wage groups contain 101, 140, and 73
   stores.
3. Confirm that the Table 4 regression sample has 357 stores.
4. Confirm Table 4's published coefficient benchmarks in the script.
5. Confirm Table 3 uses paired changes for row-3 standard errors and that its
   New Jersey-Pennsylvania change difference is approximately 2.75 FTE.
6. Keep `data/raw/public.csv` and row-level data in `data/processed/` out of
   public Git commits.

## Analysis conventions

- FTE = full-time employees + managers + 0.5 x part-time employees.
- Set wave-2 FTE to zero for permanent closures; treat temporary closures as
  missing except for Table 3 row 5, where they are set to zero.
- The treatment gap is the proportional increase needed to raise a New Jersey
  restaurant's wave-1 starting wage to $5.05; Pennsylvania and unaffected New
  Jersey restaurants have a gap of zero.
- Report differences from the original paper transparently; never change input
  values or code manually to force a match.
