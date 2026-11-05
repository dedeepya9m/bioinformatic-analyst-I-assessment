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
- Structure: I created `src/qc_exam/qc.py` to hold small, testable functions (`read_samples`, `compute_mapping_rate`, `assign_qc`, `format_rate`, `build_report`, `write_report`). `__main__.py` only handles command-line arguments, error messages and exit codes.
- Fail fast, never repair: any invalid value raises `QCValidationError` with the line number. The CLI prints `ERROR: ...` to stderr and exits with code 1. All rows are validated before the output file is written, so invalid input never produces a partial report.
- Strict integer parsing: after trimming spaces, counts must be plain digits (checked with the regex `^[0-9]+$`), so "-5", "1.5", "1e6", "+5" and blanks are rejected. Plain `int()` would wrongly accept "+5" and "1_000".
- Exact arithmetic: rates use `Decimal` instead of `float`, so comparisons at exactly 0.80 and 0.30 are exact and not affected by floating-point rounding.Output rates are rounded to 4 decimal places using Python's default Decimal rounding.
- Zero reads: `compute_mapping_rate` returns `None` (written as `NA`). LOW_MAPPING is not evaluated when there is no rate, but HIGH_DUPLICATION is still checked, so a zero-read sample can be `ZERO_READS;HIGH_DUPLICATION`.
- Column order: input columns are looked up by name, so their order in the file doesn't matter. Output columns always follow the required order.

## Tests run and results
- Ran all tests with `python -m pytest -q`: all 38 tests passed.
- Ran the tool on the provided sample file: `python -m qc_exam --input data/qc_samples.tsv --output results/qc_report.tsv`. It wrote a report for all 6 samples. S001 and S004 passed. S002, S003, S005 and S006 failed, each with the reason I expected.
- One issue I hit: running plain `pytest` at first gave a `ModuleNotFoundError`. My computer has more than one Python installed, and `pytest` was using a different one than the one where I installed my project. Running `python -m pytest` fixed this, because it makes sure the tests use the same Python as my installed code.

### Testing summary (Q2)

How to run:
```bash
python -m pip install -e '.[dev]'     # install package + pytest (Python 3.11+)
python -m pytest -q                   # run all tests
python -m qc_exam --input data/qc_samples.tsv --output results/qc_report.tsv   # generate the report
```
What the tests check:
- A normal sample: 920,000 mapped out of 1,000,000 reads gives a mapping rate of 0.92 (shown as "0.9200" in the report).
- A sample with zero reads: the tool doesn't crash, shows the rate as NA, and fails the sample with ZERO_READS.
- More mapped reads than total reads: rejected with an error.
- Negative read counts: rejected with an error.
- Missing values (empty, "NA", "nan"): rejected with an error.
- The same sample ID used twice: caught and reported, not silently dropped.
- Values exactly on the cutoffs (0.80 and 0.30): handled correctly.
- The output keeps the samples in the same order as the input.

How the tests are written:
- Several tests are parametrized, meaning one test runs on a list of different inputs. I used this for negative values, missing values, non-whole-number counts and the cutoff values.
- Each test creates its own temporary folder and files, so tests don't affect each other and give the same result every time they run.

A bug these tests are designed to catch:
- An easy mistake is writing "less than or equal to" instead of "less than" for the cutoffs. If that happened, sample S004, which sits exactly on 0.80 mapping and 0.30 duplication, would wrongly fail. My cutoff test and the full-run check on S004 would both catch this.
- A related risk is using normal computer decimals (float) instead of exact decimals (Decimal). Tiny rounding errors could push a value that should be exactly 0.80 just below it, and make a good sample fail.

## Limitations / unfinished work
- Validation stops at the first error. In a file with several problems, the user has to fix and rerun one error at a time.
- The thresholds (0.80 mapping, 0.30 duplication) are exercise-only values and are hard-coded. Real cutoffs depend on the assay (e.g. whole genome vs. exome vs. RNA-seq) and the organism.
- QC is based on only three metrics. Real sample QC would also consider things like coverage depth, base quality (e.g. % Q30), insert size and contamination.
- The tool trusts the input numbers once they pass validation. It can't tell if, for example, the duplicate rate came from the wrong tool or the wrong reference genome.

## Production improvements
- Report every validation problem in one run, with line numbers, so a broken sample sheet can be fixed in a single pass.
- Make thresholds configurable per assay (e.g. a small config file for WGS, exome and RNA-seq), and record the thresholds used in the report so every QC decision can be traced later.
- Read metrics directly from standard tool outputs (e.g. samtools flagstat for mapping, Picard MarkDuplicates for duplication) instead of a hand-made table, to avoid copy errors.