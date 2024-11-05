"""
File: doi.py
------------

For now, just counts the number of DOIs in the references.
"""
import re
import argparse
import json

DOI_REGEX = re.compile(r'10\.\d{4,9}\/[-._;()/:A-Z0-9]+', re.IGNORECASE)

def main(args):
    data = json.load(open(args.data))

    dois = 0
    for ref in data:
        if DOI_REGEX.search(ref['text']):
            dois += 1

    print(f"Number of DOIs: {dois}")
    print(f"Total number of references: {len(data)}")
    print(f"Percentage of references with DOIs: {dois / len(data):.2%}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Count the number of DOIs.')

    parser.add_argument("--data", type=str, help="Path to the JSON file containing the references.", default="data/refs.json")

    args = parser.parse_args()
    main(args)
