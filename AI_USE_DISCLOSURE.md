# AI Use Disclosure

## Where AI was used

AI assistance was used to organize the replication workflow, interpret the
course data dictionary and paper specifications, draft Python code for data
construction and analysis, format generated tables and figures, and prepare
draft report text.

## How AI-assisted work was checked

The input schema and 410-store count were checked against the supplied
dictionary. The generated Table 4 sample size and coefficients were checked
against the paper. Table 3 wage-group counts, employment definitions, closure
rules, and paired-sample uncertainty calculations were separately inspected
against the paper's table notes and the supplied data. The complete pipeline
was rerun from the documented raw-data path to confirm the outputs regenerate.
Interpretation and conclusions should be reviewed by the student before
submission.

## Important error corrected

An initial draft calculated the standard error for Table 3's row-3 employment
change as if the two survey waves were independent. Because many restaurants
appear in both waves, that calculation did not account for within-store
covariance. The final workflow instead calculates the standard error from
paired changes for stores observed in both waves; the row-3 level-change
estimate continues to use the separate wave means, as described in the paper.

AI-generated interpretations are treated as drafts rather than evidence. The
student remains responsible for the data choices, code, statistical
specification, interpretation, and conclusions.
