"""Candidate starter: implement CLI and validation here or in additional modules."""
import argparse

def main():
    parser = argparse.ArgumentParser(description="Sequencing QC report")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    raise NotImplementedError("Implement sequencing QC report generation")

if __name__ == "__main__":
    main()
