# Bioinformatics Analyst I — Sequencing QC Coding Assessment

**Timebox:** 2–3 hours of hands-on work. **Language:** Python 3.11+. **AI:** Allowed with disclosure.

## Question 1: Sequencing QC Tool

### Scenario
A bioinformatics team needs a reproducible command-line tool to validate sequencing QC data and produce a sample-level report. Use only the **synthetic** input provided. No patient information is involved.

### Input
TSV columns: `sample_id`, `total_reads`, `mapped_reads`, `duplicate_rate`. Rates are fractions between 0 and 1. Counts must be nonnegative integers. Each sample ID must be unique and nonempty.

### Requirements
1. Implement `python -m qc_exam --input data/qc_samples.tsv --output results/qc_report.tsv`.
2. Validate schema, numeric types, ranges, `mapped_reads <= total_reads`, and duplicate sample IDs. Invalid input must cause a nonzero exit with a useful error message; do not silently drop or repair rows.
3. Compute `mapping_rate = mapped_reads / total_reads`; for zero total reads output `NA` and mark `ZERO_READS`.
4. Assign `qc_status` and `qc_reasons` using these **exercise-only thresholds**: zero reads => FAIL/ZERO_READS; mapping rate < 0.80 => FAIL/LOW_MAPPING; duplicate_rate > 0.30 => FAIL/HIGH_DUPLICATION. Multiple reasons separated by `;` in the stated order. Otherwise PASS with reason `NONE`.
5. Output TSV columns, in order: `sample_id,total_reads,mapped_reads,duplicate_rate,mapping_rate,qc_status,qc_reasons`. Numeric rates should have 4 decimal places (except `NA`). Preserve input order.
6. Add tests covering ordinary, boundary, zero-read, malformed, and duplicate-ID cases. Include clear run instructions.
7. Complete `REASONING.md` and `AI_USAGE.md`; disclose material AI use. A short initial plan must be recorded **before** coding or AI assistance. If you do not use AI, say so.

### Submission
Submit a private GitHub repository link, with source, tests, `REASONING.md`, `AI_USAGE.md`, and sample output. Do not include secrets or personal AI transcripts. We may ask you to explain and modify the code in a 30–45 minute interview. Git history is supplemental evidence, not proof of authorship.

### Fairness and access
AI tools and public documentation are permitted. Candidates may request reasonable accommodations or a non-GitHub submission route. We evaluate correctness, reasoning, verification, and understanding—not whether you avoided AI. Please do not spend more than the timebox; describe unfinished work.

### Run public checks
`python -m pip install -e '.[dev]'` then `pytest -q`.

## Question 2: Unit Testing a Bioinformatics QC Pipeline (15 points)

**Estimated time:** 25–35 minutes  
**Language:** Python  
**Testing framework:** pytest  
**AI tools:** Permitted, with disclosure in `AI_USAGE.md`

### Background

Your sequencing QC pipeline calculates mapping rates and validates sample-level sequencing metrics. Before using this pipeline in a production bioinformatics workflow, you must demonstrate that its calculations and error handling behave correctly.

### Task

Write a set of automated unit tests for the functions you implemented in Question 1. These unit tests focus on individual functions and complement (do not replace) the integration/CLI tests in Question 1, requirement 6.

Create a file named:

`tests/test_candidate_qc.py`

Your tests must cover at least the following scenarios:

1. **Normal input:** Verify that 920,000 mapped reads out of 1,000,000 total reads produces a mapping rate of 0.92. (The formatted CLI output is `0.9200` with 4 decimal places per Question 1, requirement 5; assert the form matching what you test.)
2. **Zero total reads:** Verify that the pipeline handles a zero denominator without crashing and follows the documented expected behavior.
3. **Invalid mapped-read count:** Verify that mapped reads greater than total reads are detected.
4. **Negative values:** Verify that negative read counts are rejected with a nonzero exit (see Question 1, requirement 2).
5. **Missing values:** Verify that missing or null values are handled according to the documented validation policy.
6. **Duplicate sample IDs:** Verify that duplicate sample identifiers are detected rather than silently discarded.

### Additional requirements

- Use pytest.
- Include at least one parameterized test using `@pytest.mark.parametrize`.
- Use assertions that check actual outputs or error behavior, not just whether a function executes.
- Make tests independent and repeatable.
- Explain how to run the tests.
- Document one bug or potential failure mode that your tests are designed to detect (include this in the testing summary in `REASONING.md`).

### AI reasoning requirement

In `AI_USAGE.md`, describe whether AI helped you generate or review your tests, what suggestions you accepted or rejected, and how you determined that the assertions were correct.

### Deliverables

- `tests/test_candidate_qc.py`
- Any necessary test fixtures
- Updated `AI_USAGE.md`
- A brief testing summary in `REASONING.md`

Your tests will be evaluated for correctness, coverage of meaningful edge cases, clarity, and their ability to identify incorrect behavior.
