"""CLI / integration tests (Question 1, requirement 6)."""
import csv
import subprocess
import sys
from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parents[1] / "data" / "qc_samples.tsv"
HEADER = "sample_id\ttotal_reads\tmapped_reads\tduplicate_rate\n"


def run_cli(input_path, output_path):
    return subprocess.run(
        [sys.executable, "-m", "qc_exam", "--input", str(input_path), "--output", str(output_path)],
        capture_output=True, text=True,
    )


def read_tsv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def test_cli_help():
    p = subprocess.run([sys.executable, "-m", "qc_exam", "--help"], capture_output=True, text=True)
    assert p.returncode == 0
    assert "--input" in p.stdout


def test_sample_data_end_to_end(tmp_path):
    out = tmp_path / "report.tsv"
    p = run_cli(DATA, out)
    assert p.returncode == 0, p.stderr
    rows = read_tsv(out)
    assert list(rows[0].keys()) == [
        "sample_id", "total_reads", "mapped_reads", "duplicate_rate",
        "mapping_rate", "qc_status", "qc_reasons",
    ]
    got = [(r["sample_id"], r["mapping_rate"], r["qc_status"], r["qc_reasons"]) for r in rows]
    assert got == [
        ("S001", "0.9200", "PASS", "NONE"),                            # ordinary
        ("S002", "0.6000", "FAIL", "LOW_MAPPING;HIGH_DUPLICATION"),
        ("S003", "NA", "FAIL", "ZERO_READS"),                          # zero reads
        ("S004", "0.8000", "PASS", "NONE"),                            # exactly on both thresholds
        ("S005", "0.7990", "FAIL", "LOW_MAPPING;HIGH_DUPLICATION"),    # just past both
        ("S006", "0.9500", "FAIL", "HIGH_DUPLICATION"),
    ]
    assert rows[0]["duplicate_rate"] == "0.1200"


@pytest.mark.parametrize(
    "body, expected_msg",
    [
        ("S1\t100\t50\n", "expected 4 fields"),                  # missing column value
        ("S1\tabc\t50\t0.1\n", "total_reads must be a nonnegative integer"),
        ("S1\t100\t50.5\t0.1\n", "mapped_reads must be a nonnegative integer"),
        ("S1\t-100\t50\t0.1\n", "total_reads must be a nonnegative integer"),
        ("S1\t100\t150\t0.1\n", "mapped_reads (150) > total_reads (100)"),
        ("S1\t100\t50\t1.5\n", "duplicate_rate must be between 0 and 1"),
        ("S1\t100\t50\t\n", "duplicate_rate is missing"),
        ("\t100\t50\t0.1\n", "sample_id is missing"),
        ("S1\t100\t50\t0.1\nS1\t200\t150\t0.1\n", "duplicate sample_id 'S1'"),
    ],
)
def test_invalid_input_exits_nonzero(tmp_path, body, expected_msg):
    inp = tmp_path / "bad.tsv"
    inp.write_text(HEADER + body)
    out = tmp_path / "report.tsv"
    p = run_cli(inp, out)
    assert p.returncode != 0
    assert expected_msg in p.stderr
    assert not out.exists()  # no partial report written


def test_bad_header_exits_nonzero(tmp_path):
    inp = tmp_path / "bad.tsv"
    inp.write_text("sample\ttotal\tmapped\tdup\nS1\t100\t50\t0.1\n")
    p = run_cli(inp, tmp_path / "r.tsv")
    assert p.returncode != 0
    assert "header" in p.stderr


def test_missing_input_file(tmp_path):
    p = run_cli(tmp_path / "nope.tsv", tmp_path / "r.tsv")
    assert p.returncode != 0
    assert "not found" in p.stderr
