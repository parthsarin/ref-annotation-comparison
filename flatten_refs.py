"""
File: flatten_refs.py
---------------------
"""
import xml.etree.ElementTree as ET
from glob import glob
import json

def main():
    files = glob("data/*.xml")
    refs = set()
    for filename in files:
        doi = filename[5:-4]

        # read the XML file
        tree = ET.parse(filename)
        root = tree.getroot()

        # get each <mixed-citation> element in the <ref-list>
        for ref in root.findall(".//ref-list//mixed-citation"):
            # get the text of the element
            text = ''.join(ref.itertext())
            elt_text = ET.tostring(ref).decode("utf-8")

            # clean it up
            text = ' '.join(x.strip() for x in text.split("\n")).strip()
            elt_text = elt_text.strip()

            # append the source doi, marked up element, and the raw text to the list
            refs.add((doi, elt_text, text))

    refs = [{'doi': doi, 'elt_text': elt_text, 'text': text} for doi, elt_text, text in refs]
    print(f'num refs: {len(refs)}')

    # write the list of references to a JSON file
    with open("data/refs.json", "w") as f:
        json.dump(refs, f, indent=2)

if __name__ == "__main__":
    main()
