"""Unit tests for qc_exam.qc functions (Question 2)."""
from decimal import Decimal

import pytest

from qc_exam.qc import (
    QCValidationError,
    assign_qc,
    build_report,
    compute_mapping_rate,
    format_rate,
    read_samples,
)

HEADER = "sample_id\ttotal_reads\tmapped_reads\tduplicate_rate\n"


@pytest.fixture
def write_tsv(tmp_path):
    """Write a TSV body (header added) to a fresh temp file and return its path."""
    def _write(body, header=HEADER):
        p = tmp_path / "input.tsv"
        p.write_text(header + body)
        return p
    return _write


# 1. Normal input
def test_normal_mapping_rate():
    rate = compute_mapping_rate(1_000_000, 920_000)
    assert rate == Decimal("0.92")
    assert format_rate(rate) == "0.9200"


# 2. Zero total reads
def test_zero_total_reads_no_crash():
    rate = compute_mapping_rate(0, 0)
    assert rate is None
    assert format_rate(rate) == "NA"
    assert assign_qc(0, rate, Decimal("0")) == ("FAIL", "ZERO_READS")


def test_zero_reads_with_high_duplication_keeps_order():
    assert assign_qc(0, None, Decimal("0.5")) == ("FAIL", "ZERO_READS;HIGH_DUPLICATION")


# 3. Mapped > total
def test_mapped_greater_than_total_rejected(write_tsv):
    with pytest.raises(QCValidationError, match=r"mapped_reads \(101\) > total_reads \(100\)"):
        read_samples(write_tsv("S1\t100\t101\t0.1\n"))


def test_mapped_equal_total_allowed(write_tsv):
    samples = read_samples(write_tsv("S1\t100\t100\t0.1\n"))
    assert samples[0]["mapped_reads"] == 100


# 4. Negative values
@pytest.mark.parametrize("body", ["S1\t-1\t0\t0.1\n", "S1\t100\t-5\t0.1\n", "S1\t100\t50\t-0.1\n"])
def test_negative_values_rejected(write_tsv, body):
    with pytest.raises(QCValidationError):
        read_samples(write_tsv(body))


# 5. Missing / null values -> rejected (documented policy: never drop or repair)
@pytest.mark.parametrize(
    "body, field",
    [
        ("\t100\t50\t0.1\n", "sample_id"),
        ("S1\t\t50\t0.1\n", "total_reads"),
        ("S1\t100\t\t0.1\n", "mapped_reads"),
        ("S1\t100\t50\t\n", "duplicate_rate"),
        ("S1\t100\t50\tNA\n", "duplicate_rate"),
        ("S1\t100\t50\tnan\n", "duplicate_rate"),
    ],
)
def test_missing_values_rejected(write_tsv, body, field):
    with pytest.raises(QCValidationError, match=field):
        read_samples(write_tsv(body))


# 6. Duplicate sample IDs
def test_duplicate_sample_ids_detected(write_tsv):
    with pytest.raises(QCValidationError, match="duplicate sample_id 'S1'"):
        read_samples(write_tsv("S1\t100\t90\t0.1\nS2\t100\t90\t0.1\nS1\t100\t90\t0.1\n"))


# Threshold boundaries: strict < 0.80 and > 0.30
@pytest.mark.parametrize(
    "total, mapped, dup, expected",
    [
        (1000, 800, "0.30", ("PASS", "NONE")),                         # exactly on both
        (1000, 799, "0.30", ("FAIL", "LOW_MAPPING")),
        (1000, 800, "0.3001", ("FAIL", "HIGH_DUPLICATION")),
        (1000, 799, "0.31", ("FAIL", "LOW_MAPPING;HIGH_DUPLICATION")),
        (3, 0, "0", ("FAIL", "LOW_MAPPING")),
    ],
)
def test_threshold_boundaries(total, mapped, dup, expected):
    rate = compute_mapping_rate(total, mapped)
    assert assign_qc(total, rate, Decimal(dup)) == expected


@pytest.mark.parametrize("value", ["1.5", "1e6", "abc", "+5"])
def test_non_integer_counts_rejected(write_tsv, value):
    with pytest.raises(QCValidationError, match="total_reads"):
        read_samples(write_tsv(f"S1\t{value}\t0\t0.1\n"))


def test_build_report_preserves_order_and_formats(write_tsv):
    rows = build_report(read_samples(write_tsv("B\t3\t2\t0.1\nA\t0\t0\t0\n")))
    assert [r[0] for r in rows] == ["B", "A"]
    assert rows[0] == ["B", "3", "2", "0.1000", "0.6667", "FAIL", "LOW_MAPPING"]
    assert rows[1] == ["A", "0", "0", "0.0000", "NA", "FAIL", "ZERO_READS"]
