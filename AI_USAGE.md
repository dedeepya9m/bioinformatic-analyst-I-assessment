# AI interaction and decision log

AI tools used (or **None**): Claude Code

For each meaningful interaction, record:
- Task/step:
- Tool and model (if known):
- Prompt (exact or privacy-redacted):
- Relevant response summary:
- Accepted, modified, or rejected:
- Why:
- How verified:


1. To verify initial plan (REASONING.md) and this log I wrote.
- Task/step: Initial plan and AI log.
- Tool and model (if known): Claude Code, Claude Opus 5.5
- Prompt (exact or privacy-redacted): verify the summary draft I wrote in the REASONING.md and AI log and make it shorter, easily understandable.
- Relevant response summary: Drafted shorter, clear bullet points for Understanding, Assumptions, Edge cases, Test plan from the draft i wrote.
- Accepted, modified, or rejected: Modified. I rewrote the Understanding and Assumptions sections in my own words, simplified the language little more, and added Q1/Q2 labels.
- Why: I wanted the plan to reflect how I understand the task, not just AI wording.
- How verified: Checked each assumption against the README and data/DATA_DICTIONARY.md.

3. Q1: design explanation and implementation
- Task/step: Understanding how the CLI should be structured, then implementing it.
- Tool and model: Claude Code, Claude Opus 5.5
- Prompt (redacted): Asked and explained/instructed how the solution should be structured and written for Q1, then asked for the code.
- Relevant response summary: Explained the flow (validate -> compute -> write) and generated the code: strict parsing, Decimal for exact threshold comparisons, NA for zero reads, ordered reasons, nonzero exit on invalid input.
- Accepted, modified, or rejected: Accepted after review. I kept it in a separate folder, outside my source, until I had read each function, made sure its correct and run the tests myself.
- Why: It met every Q1 requirement, and the small separate functions made it easy to test and explain.
- How verified: Ran it on data/qc_samples.tsv and checked results against the thresholds (S004 = exactly 0.80 / 0.30 -> PASS; S005 = 0.799 / 0.31 -> LOW_MAPPING;HIGH_DUPLICATION). `python -m pytest -q`: 38 passed.

### 4. Q2: unit tests
- Task/step: `tests/test_candidate_qc.py` (plus Q1 CLI tests in `tests/test_public.py`).
- Tool and model: Claude Code, Claude Opus 5.5
- Prompt (redacted): Explained it how i want tests to be written and asked for tests covering the six Q2 scenarios and the Q1 test requirements.
- Relevant response summary: Generated unit tests for each scenario, parametrized tests (negatives, missing values, cutoffs, non-integer counts).
- Accepted, modified, or rejected: Accepted the required tests. Rejected an additional "extended fixture" test because it went beyond what the instructions asked.
- Why: The tests assert on actual values and error messages, not just that code runs.
- How verified: Checked expected values by hand (920000/1000000 -> "0.9200"; 2/3 -> "0.6667"); confirmed error tests use `match=` so the wrong error would fail; ran all tests.

### 5. Final check against the instructions
- Task/step: Cross-checking the submission against the README before the deadline.
- Tool and model: Claude Code, Claude Opus 5.5
- Prompt (redacted): Asked whether anything required was missing and for a review of REASONING.md.
- Relevant response summary: Flagged a missing `.gitignore`, and an inaccurate example in my parsing explanation.
- Accepted, modified, or rejected: Accepted; I made the fixes myself.
- Why: Make sure every deliverable was present and accurate.
- How verified: Compared the files pushed to GitHub against the README's Submission list.


If using an IDE assistant with automatic suggestions, summarize the meaningful suggestions, acceptance decisions, and verification; an exhaustive keystroke-level log is not expected.

I used Claude Code (Claude Opus 5.5) as a chat assistant inside VS Code, not as inline autocomplete. Its main contributions are logged in entries 1–5
above: a requirements checklist and time plan, help fixing my environment, a plan draft, generated code and tests for Q1 and Q2 and for rewording my REASONING.md in plainer language. Nothing went into my repo without my review. Generated code went into a separate folder first, and I read each function and ran the tests myself before copying it into `src/` and `tests/`. I made every commit myself.

## Reflection
What was useful? What was misleading or needed verification? What did you decide independently?

AI was most useful for turning the README into a checklist, explaining design choices (Decimal vs float at the 0.80/0.30 cutoffs, skipping low-mapping for
zero-read samples, strict regex instead of int()), fixing environment issues. I treated all AI output as unverified: I ran the tests myself (38 passed), ran the tool on the sample data, and checked the boundary samples by hand. I independently decided to test generated code in a separate folder before using it, to keep the work to what the instructions asked, and which suggestions to keep in REASONING.md, keeping only points I verified against my code and can explain.

Do not include unrelated personal conversations, private data, or credentials. Self-reported logs are not independently verified.
