"""Core validation, QC logic, and report writing for sequencing QC data."""
import csv
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

REQUIRED_COLUMNS = ["sample_id", "total_reads", "mapped_reads", "duplicate_rate"]
OUTPUT_COLUMNS = REQUIRED_COLUMNS + ["mapping_rate", "qc_status", "qc_reasons"]

# Exercise-only thresholds (not clinical criteria).
MIN_MAPPING_RATE = Decimal("0.80")
MAX_DUPLICATE_RATE = Decimal("0.30")

_INT_RE = re.compile(r"^[0-9]+$")


class QCValidationError(ValueError):
    """Raised when the input file fails validation."""


def parse_count(value, field, line):
    """Parse a nonnegative integer count. Rejects blanks, negatives, decimals, '1e6'."""
    if value is None or value.strip() == "":
        raise QCValidationError(f"line {line}: {field} is missing")
    value = value.strip()
    if not _INT_RE.match(value):
        raise QCValidationError(
            f"line {line}: {field} must be a nonnegative integer, got {value!r}"
        )
    return int(value)


def parse_rate(value, field, line):
    """Parse a fraction in [0, 1] as an exact Decimal. Rejects blanks, NaN, inf."""
    if value is None or value.strip() == "":
        raise QCValidationError(f"line {line}: {field} is missing")
    value = value.strip()
    try:
        rate = Decimal(value)
    except InvalidOperation:
        raise QCValidationError(f"line {line}: {field} must be a number, got {value!r}")
    if not rate.is_finite() or rate < 0 or rate > 1:
        raise QCValidationError(f"line {line}: {field} must be between 0 and 1, got {value!r}")
    return rate


def read_samples(path):
    """Read and validate the input TSV. Returns a list of sample dicts in input order.

    Any problem raises QCValidationError; rows are never dropped or repaired.
    """
    with open(path, newline="") as fh:
        reader = csv.reader(fh, delimiter="\t")
        header = next(reader, None)
        if header is None:
            raise QCValidationError("input file is empty")
        header = [h.strip() for h in header]
        if sorted(header) != sorted(REQUIRED_COLUMNS):
            raise QCValidationError(
                f"header must contain exactly {REQUIRED_COLUMNS}, got {header}"
            )
        idx = {name: header.index(name) for name in REQUIRED_COLUMNS}

        samples = []
        seen = {}
        for line, row in enumerate(reader, start=2):
            if not row:  # skip a fully blank line (e.g. trailing newline)
                continue
            if len(row) != len(header):
                raise QCValidationError(
                    f"line {line}: expected {len(header)} fields, got {len(row)}"
                )
            sample_id = row[idx["sample_id"]].strip()
            if sample_id == "":
                raise QCValidationError(f"line {line}: sample_id is missing")
            if sample_id in seen:
                raise QCValidationError(
                    f"line {line}: duplicate sample_id {sample_id!r} (first seen on line {seen[sample_id]})"
                )
            seen[sample_id] = line

            total = parse_count(row[idx["total_reads"]], "total_reads", line)
            mapped = parse_count(row[idx["mapped_reads"]], "mapped_reads", line)
            dup = parse_rate(row[idx["duplicate_rate"]], "duplicate_rate", line)
            if mapped > total:
                raise QCValidationError(
                    f"line {line}: mapped_reads ({mapped}) > total_reads ({total})"
                )
            samples.append(
                {"sample_id": sample_id, "total_reads": total,
                 "mapped_reads": mapped, "duplicate_rate": dup}
            )

    if not samples:
        raise QCValidationError("input file has no data rows")
    return samples


def compute_mapping_rate(total_reads, mapped_reads):
    """Return mapped/total as an exact Decimal, or None when total_reads is 0."""
    if total_reads == 0:
        return None
    return Decimal(mapped_reads) / Decimal(total_reads)


def assign_qc(total_reads, mapping_rate, duplicate_rate):
    """Return (qc_status, qc_reasons). Reasons are in the fixed stated order."""
    reasons = []
    if total_reads == 0:
        reasons.append("ZERO_READS")
    elif mapping_rate < MIN_MAPPING_RATE:
        reasons.append("LOW_MAPPING")
    if duplicate_rate > MAX_DUPLICATE_RATE:
        reasons.append("HIGH_DUPLICATION")
    if reasons:
        return "FAIL", ";".join(reasons)
    return "PASS", "NONE"


def format_rate(rate):
    """Format a rate with 4 decimal places, or 'NA' for None."""
    return "NA" if rate is None else f"{rate:.4f}"


def build_report(samples):
    """Turn validated samples into output rows (lists of strings), preserving order."""
    rows = []
    for s in samples:
        rate = compute_mapping_rate(s["total_reads"], s["mapped_reads"])
        status, reasons = assign_qc(s["total_reads"], rate, s["duplicate_rate"])
        rows.append([
            s["sample_id"], str(s["total_reads"]), str(s["mapped_reads"]),
            format_rate(s["duplicate_rate"]), format_rate(rate), status, reasons,
        ])
    return rows


def write_report(rows, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t", lineterminator="\n")
        writer.writerow(OUTPUT_COLUMNS)
        writer.writerows(rows)
