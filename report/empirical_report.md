# Card and Krueger (1994): minimum wage and employment

## Research question and motivation

This project studies whether New Jersey's April 1992 increase in its minimum wage
reduced fast-food restaurant employment relative to eastern Pennsylvania. The
paper's central policy question is whether the standard competitive-market
prediction of lower employment is supported by the survey evidence.

## Data and sample construction

The input is the course-provided `01_DID/data/public.csv` restaurant survey
(410 stores; 331 in New Jersey and 79 in Pennsylvania). The first survey was
conducted in February-March 1992 and the follow-up in November-December 1992.
Full-time-equivalent employment is full-time workers plus managers plus one-half
of part-time workers. The six permanently closed restaurants are assigned zero
follow-up employment; temporary closures are missing in the main estimates and
set to zero only in Table 3's designated sensitivity row.

The Table 4 regression sample contains 357 stores. It
requires observed wave-1 and wave-2 FTE employment and a wave-1 starting wage;
wave-2 wage is required for open/responding stores, while permanently closed
stores are retained with follow-up employment set to zero. The treatment gap is
`(5.05 - wave-1 starting wage) / wave-1 starting wage` for New Jersey stores
initially below $5.05, and zero otherwise. Models use OLS conventional standard
errors to match the paper's reported table.

## Empirical design

The core design is a two-period difference-in-differences comparison between
New Jersey (treated) and Pennsylvania (control). Table 3 reports state means,
changes, a balanced sample, and New Jersey groups split by initial wage. Table 4
regresses the change in store FTE employment on a New Jersey indicator or the
continuous initial wage gap, adding chain/ownership and regional controls.

## Core replication results

The wave-1 mean FTE employment is 20.44 in New Jersey and
23.33 in Pennsylvania. The Table 3 change-in-means difference
(New Jersey minus Pennsylvania) is 2.75 FTE employees per store.

### Table 4 regression estimates

| Model | Main coefficient | Standard error | N |
|---|---|---:|---:|
| (i) NJ dummy | 2.33 | (1.19) | 357 |
| (ii) NJ dummy | 2.30 | (1.20) | 357 |
| (iii) Initial wage gap | 15.65 | (6.08) | 357 |
| (iv) Initial wage gap | 14.92 | (6.21) | 357 |
| (v) Initial wage gap | 11.98 | (7.42) | 357 |

The estimates are close to the paper's Table 4 benchmark. Small differences
remain in the region-controlled wage-gap specification and may reflect the
course package's coding, sample conventions, or source transcription. Table 2
and Table 3 outputs are generated from the same documented input and definitions.

### Table 2: selected state means

| Variable | New Jersey | Pennsylvania | NJ-PA t-stat |
|---|---:|---:|---:|
| FTE employment, wave 1 | 20.44 (n=321) | 23.33 (n=77) | -2.35 |
| Full-time employees (%) | 32.85 (n=321) | 35.04 (n=77) | -0.73 |
| Starting wage, wave 1 ($) | 4.61 (n=314) | 4.63 (n=76) | -0.41 |
| Starting wage = $4.25 (%) | 30.51 (n=331) | 32.91 (n=79) | -0.41 |
| Full meal price, wave 1 ($) | 3.35 (n=311) | 3.04 (n=76) | 3.79 |
| FTE employment, wave 2 | 21.03 (n=319) | 21.17 (n=77) | -0.12 |
| Starting wage, wave 2 ($) | 5.08 (n=318) | 4.62 (n=71) | 19.71 |
| Starting wage = $5.05, wave 2 (%) | 85.50 (n=331) | 1.27 (n=79) | 20.96 |
| Full meal price, wave 2 ($) | 3.41 (n=305) | 3.03 (n=71) | 4.73 |

Category-share rows for starting wages use all sampled stores as the denominator;
missing second-wave wages are not counted in either wage category. Table 2's
full output, including store composition, standard errors, and tests, is in
`output/tables/table2_summary.csv`.

### Table 3: employment comparisons

| Table 3 row | Comparison | Estimate (FTE) | SE |
|---|---|---:|---:|
| 1 | New Jersey - Pennsylvania | -2.89 | (1.44) |
| 2 | New Jersey - Pennsylvania | -0.14 | (1.08) |
| 3 | New Jersey - Pennsylvania | 2.75 | (1.80) |
| 4 | New Jersey - Pennsylvania | 2.75 | (1.34) |
| 5 | New Jersey - Pennsylvania | 2.51 | (1.35) |
| 3 | NJ low wage - high wage | 3.36 | (1.99) |
| 3 | NJ midrange wage - high wage | 2.91 | (1.90) |

The low-, middle-, and high-initial-wage New Jersey groups contain 101, 140, and
73 stores before outcome-specific missingness. Full subgroup means and all
reported comparisons are in `output/tables/table3_employment.csv`.

### Figure 1

![Starting-wage distributions](output/figures/figure1_wage_distribution.png)

The figure shows the percentage distribution of observed starting wages by state
in each survey wave. Wave-2 wages are not imputed for closures or nonrespondents.

## Independent extension: ownership heterogeneity

As an independent extension, the project tests whether the NJ-policy employment
effect differs between company-owned and franchise-owned restaurants. The
two-wave store-level model includes store fixed effects, a wave indicator, and
NJ-by-post interactions for ownership status; standard errors are clustered by
store. The additional NJ-by-post interaction for company ownership is
-1.04 (clustered SE 3.40,
p=0.760). The estimated NJ-by-post effect among
franchise-owned stores is 3.13. This is an exploratory heterogeneity
test, not evidence that ownership status was randomly assigned.

## Validation, limitations, and conclusion

The workflow checks the 410-record input, the expected 357-observation Table 4
sample, and the key published Table 4 coefficients. Table 2's means use
variable-specific nonmissing observations. The main limitations are the
nonrandom state-level treatment, one pre-treatment wave, a modest store sample,
survey measurement error, and limited external validity beyond the sampled
chains and regions. Differences in data coverage and closure handling are
reported rather than hidden.

## AI-use disclosure

AI assistance was used to organize the replication workflow, draft analysis
code, and help interpret the data dictionary and paper specifications. The
script's formulas, sample size, and Table 4 estimates were checked against the
supplied paper; generated tables and figures are reproducible from the input.
The student should independently verify the economic interpretation, review all
sample decisions, and document any further corrections or rejected suggestions.
