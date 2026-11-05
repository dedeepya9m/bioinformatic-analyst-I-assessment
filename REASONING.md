# Reasoning and validation

## Initial plan (complete before coding/AI)

Understanding:
- (Q1) Build a CLI tool that reads a sample-level QC TSV, validates it strictly, computes mapping rate (mapped reads divided by total reads), assigns PASS/FAIL with ordered reasons, and writes a TSV report in input order.
- (Q1) The results are written to a new table in the same order as the input.
- (Q1) If anything in the input is wrong, the tool stops with a clear error message.
- (Q1) It never skips or quietly fixes bad rows.
- (Q2) Write pytest unit tests for the individual Q1 functions (mapping rate, zero reads, mapped > total, negatives, missing values, duplicate IDs), separate from the CLI tests.

Assumptions:
- The file must have exactly the four expected columns. Extra or missing columns count as an error, but the column order doesn't matter.
- Read counts must be whole, non-negative numbers. Things like "-5", "1.5", "1e6", "+5" or an empty box are rejected.
- The duplicate rate must be a real number between 0 and 1. Empty, "NA" or "nan" are rejected. I won't fill in missing values.
- Extra spaces around values are ignored. A blank sample ID is an error.
- A file with no samples (only a header, or completely empty) is an error.
- Both rates (mapping and duplicate) are shown with 4 decimal places.
- The cutoffs are strict: only a mapping rate below 0.80 fails, and only a duplicate rate above 0.30 fails. A sample sitting exactly on 0.80 or 0.30 passes.
- If a sample has zero reads, its mapping rate is NA and it fails with ZERO_READS. Low mapping can't be judged without a rate, but high duplication is still checked.

Likely edge cases:
- total_reads = 0 (division by zero)
- values exactly on thresholds and just past them
- mapped_reads > total_reads; mapped_reads == total_reads (valid)
- negative, non-integer, missing, NaN values
- duplicate or empty sample IDs
- wrong/missing header, wrong number of fields, missing input file
- floating-point error at thresholds -> plan to use exact arithmetic (Decimal)

Test plan:
- (Q1) CLI tests (tests/test_public.py): run on data/qc_samples.tsv and assert every output row; parametrized malformed files assert nonzero exit + message + no output file written.
- (Q2) Unit tests (tests/test_candidate_qc.py): mapping rate (920000/1000000 -> 0.9200), zero reads, mapped > total, negatives, missing values, duplicate IDs, threshold boundaries (parametrized), input order preserved.

## Implementation decisions

## Tests run and results

## Limitations / unfinished work

## Production improvements
