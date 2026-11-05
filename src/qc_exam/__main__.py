"""CLI: python -m qc_exam --input data/qc_samples.tsv --output results/qc_report.tsv"""
import argparse
import sys

from qc_exam.qc import QCValidationError, build_report, read_samples, write_report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Sequencing QC report")
    parser.add_argument("--input", required=True, help="input QC TSV")
    parser.add_argument("--output", required=True, help="output report TSV")
    args = parser.parse_args(argv)

    try:
        samples = read_samples(args.input)
    except FileNotFoundError:
        print(f"ERROR: input file not found: {args.input}", file=sys.stderr)
        return 1
    except QCValidationError as e:
        print(f"ERROR: invalid input: {e}", file=sys.stderr)
        return 1

    write_report(build_report(samples), args.output)
    print(f"Wrote {len(samples)} samples to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
