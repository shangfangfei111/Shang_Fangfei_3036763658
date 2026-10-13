from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.formula.api as smf


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "01_DID" / "data" / "public.csv"
TABLES = ROOT / "output" / "tables"
FIGURES = ROOT / "output" / "figures"
PROCESSED = ROOT / "output" / "processed_data.csv"

MINIMUM_WAGE = 5.05
PERMANENT_CLOSURE = 3
TEMPORARY_CLOSURES = (2, 4, 5)
CHAINS = {
    1: "Burger King",
    2: "KFC",
    3: "Roy Rogers",
    4: "Wendy's",
}

REQUIRED_COLUMNS = {
    "SHEET",
    "CHAIN",
    "CO_OWNED",
    "STATE",
    "SOUTHJ",
    "CENTRALJ",
    "PA1",
    "PA2",
    "EMPFT",
    "EMPPT",
    "NMGRS",
    "WAGE_ST",
    "BONUS",
    "HRSOPEN",
    "PSODA",
    "PFRY",
    "PENTREE",
    "STATUS2",
    "EMPFT2",
    "EMPPT2",
    "NMGRS2",
    "WAGE_ST2",
    "SPECIAL2",
    "HRSOPEN2",
    "PSODA2",
    "PFRY2",
    "PENTREE2",
}


def load_data() -> pd.DataFrame:
    if not INPUT.is_file():
        raise FileNotFoundError(
            f"Required input is missing: {INPUT}. "
            "Extract the course-provided 01_DID package without renaming its files."
        )

    data = pd.read_csv(INPUT)
    missing = REQUIRED_COLUMNS.difference(data.columns)
    if missing:
        raise ValueError(f"public.csv is missing required columns: {sorted(missing)}")
    if len(data) != 410:
        raise ValueError(f"Expected 410 survey records, found {len(data)}.")

    data["fte1"] = data["EMPFT"] + data["NMGRS"] + 0.5 * data["EMPPT"]
    data["fte2"] = data["EMPFT2"] + data["NMGRS2"] + 0.5 * data["EMPPT2"]
    data.loc[data["STATUS2"].eq(PERMANENT_CLOSURE), "fte2"] = 0.0
    data.loc[data["STATUS2"].isin(TEMPORARY_CLOSURES), "fte2"] = np.nan
    data["change_fte"] = data["fte2"] - data["fte1"]
    data["wage_gap"] = 0.0
    affected = data["STATE"].eq(1) & data["WAGE_ST"].lt(MINIMUM_WAGE)
    data.loc[affected, "wage_gap"] = (
        MINIMUM_WAGE - data.loc[affected, "WAGE_ST"]
    ) / data.loc[affected, "WAGE_ST"]
    data["meal_price1"] = data[["PSODA", "PFRY", "PENTREE"]].sum(
        axis=1, min_count=3
    )
    data["meal_price2"] = data[["PSODA2", "PFRY2", "PENTREE2"]].sum(
        axis=1, min_count=3
    )
    data["fulltime_share1"] = (data["EMPFT"] / data["fte1"]).where(data["fte1"] > 0)
    data["fulltime_share2"] = (data["EMPFT2"] / data["fte2"]).where(data["fte2"] > 0)
    data["post_wage_505"] = data["WAGE_ST2"].eq(MINIMUM_WAGE).astype(float)
    data.loc[data["WAGE_ST2"].isna(), "post_wage_505"] = np.nan
    data["wage_group"] = pd.Series(pd.NA, index=data.index, dtype="string")
    nj = data["STATE"].eq(1)
    data.loc[nj & np.isclose(data["WAGE_ST"], 4.25), "wage_group"] = "Wage = $4.25"
    data.loc[nj & data["WAGE_ST"].between(4.26, 4.99), "wage_group"] = (
        "Wage $4.26-$4.99"
    )
    data.loc[nj & data["WAGE_ST"].ge(5.00), "wage_group"] = "Wage >= $5.00"
    data["temporary_zero_fte2"] = data["fte2"]
    temporary = data["STATUS2"].isin(TEMPORARY_CLOSURES)
    data.loc[temporary, "temporary_zero_fte2"] = 0.0
    return data


def mean_se(values: pd.Series) -> tuple[float, float, int]:
    clean = values.dropna()
    if clean.empty:
        return math.nan, math.nan, 0
    se = clean.std(ddof=1) / math.sqrt(len(clean)) if len(clean) > 1 else math.nan
    return float(clean.mean()), float(se), int(len(clean))


def difference_test(left: pd.Series, right: pd.Series) -> tuple[float, float]:
    left = left.dropna()
    right = right.dropna()
    if len(left) < 2 or len(right) < 2:
        return math.nan, math.nan
    result = stats.ttest_ind(left, right, equal_var=True, nan_policy="omit")
    return float(result.statistic), float(result.pvalue)


def create_table2(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    def add_row(label: str, nj_values: pd.Series, pa_values: pd.Series) -> None:
        nj_mean, nj_se, nj_n = mean_se(nj_values)
        pa_mean, pa_se, pa_n = mean_se(pa_values)
        t_stat, p_value = difference_test(nj_values, pa_values)
        rows.append(
            {
                "variable": label,
                "NJ_mean": nj_mean,
                "NJ_se": nj_se,
                "NJ_n": nj_n,
                "PA_mean": pa_mean,
                "PA_se": pa_se,
                "PA_n": pa_n,
                "NJ_minus_PA_t": t_stat,
                "p_value": p_value,
            }
        )

    for chain, label in CHAINS.items():
        indicator = data["CHAIN"].eq(chain).astype(float) * 100
        add_row(
            f"Store type: {label} (%)",
            indicator[data["STATE"].eq(1)],
            indicator[data["STATE"].eq(0)],
        )
    company_owned = data["CO_OWNED"].eq(1).astype(float) * 100
    add_row(
        "Company-owned (%)",
        company_owned[data["STATE"].eq(1)],
        company_owned[data["STATE"].eq(0)],
    )

    wave1_metrics = [
        ("FTE employment, wave 1", "fte1"),
        ("Full-time employees (%)", "fulltime_share1"),
        ("Starting wage, wave 1 ($)", "WAGE_ST"),
        ("Starting wage = $4.25 (%)", "WAGE_ST"),
        ("Full meal price, wave 1 ($)", "meal_price1"),
        ("Weekday hours open, wave 1", "HRSOPEN"),
        ("Recruiting bonus, wave 1 (%)", "BONUS"),
    ]
    for label, column in wave1_metrics:
        values = data[column]
        if label == "Starting wage = $4.25 (%)":
            values = values.eq(4.25).astype(float) * 100
        elif label.endswith("(%)"):
            values = values.astype(float) * 100
        add_row(
            label,
            values[data["STATE"].eq(1)],
            values[data["STATE"].eq(0)],
        )

    wave2_metrics = [
        ("FTE employment, wave 2", "fte2"),
        ("Full-time employees, wave 2 (%)", "fulltime_share2"),
        ("Starting wage, wave 2 ($)", "WAGE_ST2"),
        ("Starting wage = $4.25, wave 2 (%)", "WAGE_ST2"),
        ("Starting wage = $5.05, wave 2 (%)", "post_wage_505"),
        ("Full meal price, wave 2 ($)", "meal_price2"),
        ("Weekday hours open, wave 2", "HRSOPEN2"),
        ("Recruiting/special program, wave 2 (%)", "SPECIAL2"),
    ]
    for label, column in wave2_metrics:
        values = data[column]
        if label == "Starting wage = $4.25, wave 2 (%)":
            values = values.eq(4.25).astype(float) * 100
        elif label.endswith("(%)") and column == "SPECIAL2":
            values = values.astype(float) * 100
        elif label.endswith("(%)") and column == "fulltime_share2":
            values = values.astype(float) * 100
        elif column == "post_wage_505":
            values = values.fillna(0) * 100
        add_row(
            label,
            values[data["STATE"].eq(1)],
            values[data["STATE"].eq(0)],
        )
    return pd.DataFrame(rows)


def create_table3(data: pd.DataFrame) -> pd.DataFrame:
    groups: dict[str, pd.Series] = {
        "Pennsylvania": data["STATE"].eq(0),
        "New Jersey": data["STATE"].eq(1),
        "NJ: Wage = $4.25": data["wage_group"].eq("Wage = $4.25"),
        "NJ: Wage $4.26-$4.99": data["wage_group"].eq("Wage $4.26-$4.99"),
        "NJ: Wage >= $5.00": data["wage_group"].eq("Wage >= $5.00"),
    }
    metrics: dict[tuple[str, str], tuple[float, float, int]] = {}
    for group, mask in groups.items():
        for wave, column in (("1", "fte1"), ("2", "fte2")):
            metrics[(wave, group)] = mean_se(data.loc[mask, column])

        before = data.loc[mask, "fte1"]
        after = data.loc[mask, "fte2"]
        before_mean, before_se, before_n = mean_se(before)
        after_mean, after_se, after_n = mean_se(after)
        metrics[("3", group)] = (
            after_mean - before_mean,
            math.sqrt(before_se**2 + after_se**2),
            min(before_n, after_n),
        )

        balanced = data.loc[mask, ["fte1", "fte2"]].dropna()
        delta = balanced["fte2"] - balanced["fte1"]
        metrics[("4", group)] = mean_se(delta)

        zero_temp = data.loc[mask, ["fte1", "temporary_zero_fte2"]].dropna()
        zero_delta = zero_temp["temporary_zero_fte2"] - zero_temp["fte1"]
        metrics[("5", group)] = mean_se(zero_delta)

    rows: list[dict[str, object]] = []
    for table_row, description in (
        ("1", "FTE employment before, all available observations"),
        ("2", "FTE employment after, all available observations"),
        ("3", "Change in mean FTE employment"),
        ("4", "Change in FTE employment, balanced sample"),
        ("5", "Change in FTE employment, temporary closures set to zero"),
    ):
        wave = table_row if table_row in {"1", "2"} else table_row
        for group in groups:
            estimate, se, n = metrics[(wave, group)]
            rows.append(
                {
                    "table_row": table_row,
                    "description": description,
                    "comparison": f"Mean: {group}",
                    "estimate": estimate,
                    "standard_error": se,
                    "n": n,
                }
            )

        if table_row in {"1", "2", "3", "4", "5"}:
            comparisons = [
                ("New Jersey - Pennsylvania", "New Jersey", "Pennsylvania"),
                (
                    "NJ low wage - high wage",
                    "NJ: Wage = $4.25",
                    "NJ: Wage >= $5.00",
                ),
                (
                    "NJ midrange wage - high wage",
                    "NJ: Wage $4.26-$4.99",
                    "NJ: Wage >= $5.00",
                ),
            ]
            for label, left_group, right_group in comparisons:
                left_mean, left_se, left_n = metrics[(wave, left_group)]
                right_mean, right_se, right_n = metrics[(wave, right_group)]
                rows.append(
                    {
                        "table_row": table_row,
                        "description": description,
                        "comparison": label,
                        "estimate": left_mean - right_mean,
                        "standard_error": math.sqrt(left_se**2 + right_se**2),
                        "n": min(left_n, right_n),
                    }
                )
    return pd.DataFrame(rows)


def create_table4(data: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    eligible = data["fte1"].notna() & data["fte2"].notna() & data["WAGE_ST"].notna()
    has_wave2_wage_or_closed = data["WAGE_ST2"].notna() | data[
        "STATUS2"
    ].eq(PERMANENT_CLOSURE)
    sample = data.loc[eligible & has_wave2_wage_or_closed].copy()
    if len(sample) != 357:
        raise ValueError(f"Expected 357 Table 4 observations, found {len(sample)}.")

    specifications = [
        ("(i)", "change_fte ~ STATE", "NJ dummy", "No", "No"),
        (
            "(ii)",
            "change_fte ~ STATE + C(CHAIN) + CO_OWNED",
            "NJ dummy",
            "Chain and ownership",
            "No",
        ),
        ("(iii)", "change_fte ~ wage_gap", "Initial wage gap", "No", "No"),
        (
            "(iv)",
            "change_fte ~ wage_gap + C(CHAIN) + CO_OWNED",
            "Initial wage gap",
            "Chain and ownership",
            "No",
        ),
        (
            "(v)",
            "change_fte ~ wage_gap + C(CHAIN) + CO_OWNED + SOUTHJ + CENTRALJ + PA1 + PA2",
            "Initial wage gap",
            "Chain and ownership",
            "Yes",
        ),
    ]
    rows: list[dict[str, object]] = []
    models: dict[str, object] = {}
    for column, formula, term, controls, region_controls in specifications:
        model = smf.ols(formula, data=sample).fit()
        coefficient = "STATE" if term == "NJ dummy" else "wage_gap"
        p_value = math.nan
        if controls != "No" or region_controls == "Yes":
            tested = [name for name in model.params.index if name not in ("Intercept", coefficient)]
            restriction = ", ".join(f"{name} = 0" for name in tested)
            p_value = float(model.f_test(restriction).pvalue)
        rows.append(
            {
                "model": column,
                "main_regressor": term,
                "coefficient": float(model.params[coefficient]),
                "standard_error": float(model.bse[coefficient]),
                "t_statistic": float(model.tvalues[coefficient]),
                "p_value": float(model.pvalues[coefficient]),
                "N": int(model.nobs),
                "chain_ownership_controls": controls,
                "region_controls": region_controls,
                "joint_control_F_test_p": p_value,
                "dependent_variable_mean": float(sample["change_fte"].mean()),
                "dependent_variable_sd": float(sample["change_fte"].std(ddof=1)),
            }
        )
        models[column] = model

    expected = np.array([2.33, 2.30, 15.65, 14.92, 11.91])
    actual = np.array([row["coefficient"] for row in rows])
    if not np.allclose(actual, expected, atol=0.20):
        raise ValueError(
            "Table 4 estimates do not match the supplied-paper benchmark within "
            f"0.20: found {actual.tolist()}."
        )
    return pd.DataFrame(rows), {"sample": sample, "models": models}


def create_ownership_extension(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    sample = data.dropna(subset=["fte1", "fte2", "CO_OWNED", "STATE"]).copy()
    panel = pd.concat(
        [
            sample.assign(post=0, fte=sample["fte1"]),
            sample.assign(post=1, fte=sample["fte2"]),
        ],
        ignore_index=True,
    )
    panel["nj"] = panel["STATE"].astype(int)
    panel["owned"] = panel["CO_OWNED"].astype(int)
    model = smf.ols(
        "fte ~ C(SHEET) + post + nj:post + owned:post + nj:post:owned",
        data=panel,
    ).fit(cov_type="cluster", cov_kwds={"groups": panel["SHEET"]})

    interaction_term = "nj:post:owned"
    rows = [
        {
            "term": "NJ x post (franchise-owned baseline)",
            "estimate": float(model.params["nj:post"]),
            "clustered_standard_error": float(model.bse["nj:post"]),
            "p_value": float(model.pvalues["nj:post"]),
            "N_store_waves": int(model.nobs),
            "N_stores": int(sample["SHEET"].nunique()),
        },
        {
            "term": "Additional NJ x post effect, company-owned",
            "estimate": float(model.params[interaction_term]),
            "clustered_standard_error": float(model.bse[interaction_term]),
            "p_value": float(model.pvalues[interaction_term]),
            "N_store_waves": int(model.nobs),
            "N_stores": int(sample["SHEET"].nunique()),
        },
        {
            "term": "NJ x post (company-owned total)",
            "estimate": float(model.params["nj:post"] + model.params[interaction_term]),
            "clustered_standard_error": math.nan,
            "p_value": math.nan,
            "N_store_waves": int(model.nobs),
            "N_stores": int(sample["SHEET"].nunique()),
        },
    ]
    estimates = pd.DataFrame(rows)

    subgroup_rows = []
    for owned, owner_label in ((0, "Franchise-owned"), (1, "Company-owned")):
        for state, state_label in ((0, "Pennsylvania"), (1, "New Jersey")):
            subset = sample.loc[
                sample["CO_OWNED"].eq(owned) & sample["STATE"].eq(state)
            ]
            for wave, column in (("Wave 1", "fte1"), ("Wave 2", "fte2")):
                mean, se, n = mean_se(subset[column])
                subgroup_rows.append(
                    {
                        "ownership": owner_label,
                        "state": state_label,
                        "wave": wave,
                        "mean_fte": mean,
                        "standard_error": se,
                        "N": n,
                    }
                )
    return estimates, pd.DataFrame(subgroup_rows)


def create_figure1(data: pd.DataFrame) -> Path:
    output = FIGURES / "figure1_wage_distribution.png"
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharey=True)
    bins = np.arange(3.75, 8.76, 0.25)
    colors = {0: "#315b7d", 1: "#d36b3d"}
    labels = {0: "Pennsylvania", 1: "New Jersey"}
    for ax, wave, column, title in (
        (axes[0], "Wave 1", "WAGE_ST", "February-March 1992"),
        (axes[1], "Wave 2", "WAGE_ST2", "November-December 1992"),
    ):
        for state in (0, 1):
            values = data.loc[data["STATE"].eq(state), column].dropna()
            weights = np.full(len(values), 100 / len(values)) if len(values) else None
            ax.hist(
                values,
                bins=bins,
                weights=weights,
                alpha=0.55,
                color=colors[state],
                edgecolor="white",
                linewidth=0.5,
                label=labels[state],
            )
        ax.set_title(title)
        ax.set_xlabel("Starting wage ($ per hour)")
        ax.grid(axis="y", alpha=0.2)
    axes[0].set_ylabel("Stores in wage bin (%)")
    axes[1].legend(frameon=False)
    fig.suptitle("Starting-wage distributions before and after the New Jersey increase")
    fig.tight_layout()
    fig.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output


def format_number(value: object, digits: int = 2) -> str:
    if pd.isna(value):
        return ""
    return f"{float(value):.{digits}f}"


def create_report(
    data: pd.DataFrame,
    table2: pd.DataFrame,
    table3: pd.DataFrame,
    table4: pd.DataFrame,
    extension: pd.DataFrame,
) -> None:
    table2_lines = [
        "| Variable | New Jersey | Pennsylvania | NJ-PA t-stat |",
        "|---|---:|---:|---:|",
    ]
    table2_variables = [
        "FTE employment, wave 1",
        "Full-time employees (%)",
        "Starting wage, wave 1 ($)",
        "Starting wage = $4.25 (%)",
        "Full meal price, wave 1 ($)",
        "FTE employment, wave 2",
        "Starting wage, wave 2 ($)",
        "Starting wage = $5.05, wave 2 (%)",
        "Full meal price, wave 2 ($)",
    ]
    for variable in table2_variables:
        row = table2.loc[table2["variable"].eq(variable)].iloc[0]
        table2_lines.append(
            f"| {variable} | {format_number(row['NJ_mean'])} "
            f"(n={int(row['NJ_n'])}) | {format_number(row['PA_mean'])} "
            f"(n={int(row['PA_n'])}) | {format_number(row['NJ_minus_PA_t'])} |"
        )

    table3_lines = [
        "| Table 3 row | Comparison | Estimate (FTE) | SE |",
        "|---|---|---:|---:|",
    ]
    table3_selections = [
        ("1", "New Jersey - Pennsylvania"),
        ("2", "New Jersey - Pennsylvania"),
        ("3", "New Jersey - Pennsylvania"),
        ("4", "New Jersey - Pennsylvania"),
        ("5", "New Jersey - Pennsylvania"),
        ("3", "NJ low wage - high wage"),
        ("3", "NJ midrange wage - high wage"),
    ]
    for row_number, comparison in table3_selections:
        row = table3.loc[
            table3["table_row"].eq(row_number)
            & table3["comparison"].eq(comparison)
        ].iloc[0]
        table3_lines.append(
            f"| {row_number} | {comparison} | {format_number(row['estimate'])} | "
            f"({format_number(row['standard_error'])}) |"
        )

    table4_lines = [
        "| Model | Main coefficient | Standard error | N |",
        "|---|---|---:|---:|",
    ]
    for _, row in table4.iterrows():
        table4_lines.append(
            f"| {row['model']} {row['main_regressor']} | "
            f"{format_number(row['coefficient'])} | "
            f"({format_number(row['standard_error'])}) | {int(row['N'])} |"
        )

    did = table3.loc[
        (table3["table_row"].eq("3"))
        & table3["comparison"].eq("New Jersey - Pennsylvania"),
        "estimate",
    ].iloc[0]
    franchise = extension.loc[
        extension["term"].eq("NJ x post (franchise-owned baseline)"),
        "estimate",
    ].iloc[0]
    heterogeneity = extension.loc[
        extension["term"].eq("Additional NJ x post effect, company-owned")
    ].iloc[0]
    nj_before = mean_se(data.loc[data["STATE"].eq(1), "fte1"])[0]
    pa_before = mean_se(data.loc[data["STATE"].eq(0), "fte1"])[0]
    text = f"""# Card and Krueger (1994): minimum wage and employment

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

The Table 4 regression sample contains {int(table4['N'].iloc[0])} stores. It
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

The wave-1 mean FTE employment is {nj_before:.2f} in New Jersey and
{pa_before:.2f} in Pennsylvania. The Table 3 change-in-means difference
(New Jersey minus Pennsylvania) is {did:.2f} FTE employees per store.

### Table 4 regression estimates

{chr(10).join(table4_lines)}

The estimates are close to the paper's Table 4 benchmark. Small differences
remain in the region-controlled wage-gap specification and may reflect the
course package's coding, sample conventions, or source transcription. Table 2
and Table 3 outputs are generated from the same documented input and definitions.

### Table 2: selected state means

{chr(10).join(table2_lines)}

Category-share rows for starting wages use all sampled stores as the denominator;
missing second-wave wages are not counted in either wage category. Table 2's
full output, including store composition, standard errors, and tests, is in
`output/tables/table2_summary.csv`.

### Table 3: employment comparisons

{chr(10).join(table3_lines)}

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
{heterogeneity['estimate']:.2f} (clustered SE {heterogeneity['clustered_standard_error']:.2f},
p={heterogeneity['p_value']:.3f}). The estimated NJ-by-post effect among
franchise-owned stores is {franchise:.2f}. This is an exploratory heterogeneity
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
"""
    (ROOT / "report").mkdir(parents=True, exist_ok=True)
    (ROOT / "report" / "empirical_report.md").write_text(text, encoding="utf-8")


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    data = load_data()
    table2 = create_table2(data)
    table3 = create_table3(data)
    table4, _ = create_table4(data)
    ownership, ownership_groups = create_ownership_extension(data)

    table2.to_csv(TABLES / "table2_summary.csv", index=False)
    table3.to_csv(TABLES / "table3_employment.csv", index=False)
    table4.to_csv(TABLES / "table4_regressions.csv", index=False)
    ownership.to_csv(TABLES / "ownership_heterogeneity.csv", index=False)
    ownership_groups.to_csv(TABLES / "ownership_group_means.csv", index=False)
    data.to_csv(PROCESSED, index=False)
    create_figure1(data)
    create_report(data, table2, table3, table4, ownership)

    print(f"Input observations: {len(data)}")
    print(f"Table 4 observations: {int(table4['N'].iloc[0])}")
    print("Table 4 estimates:")
    print(table4[["model", "main_regressor", "coefficient", "standard_error"]].to_string(index=False))
    print("Ownership heterogeneity:")
    print(ownership.to_string(index=False))
    print(f"Outputs written under: {ROOT / 'output'}")


if __name__ == "__main__":
    main()
