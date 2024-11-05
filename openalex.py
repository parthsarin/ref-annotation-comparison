"""
File: openalex.py
-----------------

Annotates the references with the OpenAlex API.
"""
import json
import requests
from dotenv import load_dotenv
import argparse
from tqdm import tqdm
import xml.etree.ElementTree as ET
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

TRAINING_REF = {
  "doi": "10.12688%2Fopenreseurope.15810.2",
  "elt_text": "<mixed-citation publication-type=\"journal\">\n                    <person-group person-group-type=\"author\">\n\n                        <name name-style=\"western\">\n                            <surname>Krug</surname>\n                            <given-names>K</given-names>\n                        </name>\n\n                        <name name-style=\"western\">\n                            <surname>Jaehnig</surname>\n                            <given-names>EJ</given-names>\n                        </name>\n\n                        <name name-style=\"western\">\n                            <surname>Satpathy</surname>\n                            <given-names>S</given-names>\n                        </name>\n\n                        <etal />\n               </person-group>:\n                    <article-title>Proteogenomic Landscape of Breast Cancer Tumorigenesis and Targeted Therapy.</article-title>\n                    <source>\n\n                        <italic toggle=\"yes\">Cell.</italic>\n               </source>\n               <year>2020</year>;<volume>183</volume>(<issue>5</issue>):<fpage>1436</fpage>&#8211;<lpage>1456</lpage>.\n                    <elocation-id>e31</elocation-id>.\n                    <pub-id pub-id-type=\"pmid\">33212010</pub-id>\n                    <pub-id pub-id-type=\"doi\">10.1016/j.cell.2020.10.036</pub-id>\n                    <pub-id pub-id-type=\"pmcid\">8077737</pub-id>\n                </mixed-citation>",
  "text": "Krug K    Jaehnig EJ    Satpathy S    : Proteogenomic Landscape of Breast Cancer Tumorigenesis and Targeted Therapy.   Cell.  2020;183(5):1436\u20131456. e31. 33212010 10.1016/j.cell.2020.10.036 8077737"
}

def openalex_to_mixed_citation(data):
    # Create the root element for mixed-citation
    mixed_citation = ET.Element('mixed-citation', attrib={'publication-type': 'journal'})

    # Create the person-group for authors
    person_group = ET.SubElement(mixed_citation, 'person-group', attrib={'person-group-type': 'author'})

    for author in data.get('authorships', []):
        name = ET.SubElement(person_group, 'name', attrib={'name-style': 'western'})

        # Split the author display name into surname and given-names
        full_name = author['author']['display_name']
        if ',' in full_name:
            surname, given_names = full_name.split(',', 1)
        else:
            parts = full_name.split()
            surname = parts[-1]
            given_names = ' '.join(parts[:-1])

        ET.SubElement(name, 'surname').text = surname.strip()
        ET.SubElement(name, 'given-names').text = given_names.strip()

    # Add <etal /> if there are more authors
    if len(data['authorships']) > 3:
        ET.SubElement(person_group, 'etal')

    # Add article title
    article_title = ET.SubElement(mixed_citation, 'article-title')
    article_title.text = data['title'] + '.'

    # Add journal source
    source = ET.SubElement(mixed_citation, 'source')
    source.text = data['primary_location']['source']['display_name'] + '.'

    # Add year
    year = ET.SubElement(mixed_citation, 'year')
    year.text = str(data['publication_year'])

    # Add volume, issue, and pages if available
    if 'volume' in data:
        volume = ET.SubElement(mixed_citation, 'volume')
        volume.text = str(data['volume'])

    if 'issue' in data:
        issue = ET.SubElement(mixed_citation, 'issue')
        issue.text = str(data['issue'])

    if 'first_page' in data and 'last_page' in data:
        fpage = ET.SubElement(mixed_citation, 'fpage')
        fpage.text = str(data['first_page'])

        lpage = ET.SubElement(mixed_citation, 'lpage')
        lpage.text = str(data['last_page'])

    # Add pub-ids
    if 'pmid' in data['ids']:
        pmid = ET.SubElement(mixed_citation, 'pub-id', attrib={'pub-id-type': 'pmid'})
        pmid.text = data['ids']['pmid'].split('/')[-1]

    if 'doi' in data['ids']:
        doi = ET.SubElement(mixed_citation, 'pub-id', attrib={'pub-id-type': 'doi'})
        doi.text = data['ids']['doi'].split('/')[-1]

    if 'pmcid' in data['ids']:
        pmcid = ET.SubElement(mixed_citation, 'pub-id', attrib={'pub-id-type': 'pmcid'})
        pmcid.text = data['ids']['pmcid'].split('/')[-1]

    # Convert to string
    citation_xml = ET.tostring(mixed_citation, encoding='unicode')
    return citation_xml


def get_reference(ref, idx):
    r = requests.get(f'https://api.openalex.org/works?search={ref["text"]}')
    r = r.json()

    try:
        hit = r['results'][0]
        prediction = openalex_to_mixed_citation(hit)
    except (IndexError, KeyError):
        prediction = "<mixed-citation></mixed-citation>"

    result = {
        "doi": ref['doi'],
        "text": ref['text'],
        "elt_text": ref['elt_text'],
        "prediction": prediction
    }
    return result


def main(args):
    data = json.load(open(args.data))
    data = [ref for ref in data if (ref['doi'], ref['text']) != (TRAINING_REF['doi'], TRAINING_REF['text'])]

    try:
        annotated_refs = json.load(open(args.output))
        completed = set((ref['doi'], ref['text']) for ref in annotated_refs)
    except FileNotFoundError:
        annotated_refs = []
        completed = set()

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_ref = {executor.submit(get_reference, ref, i): ref for i, ref in enumerate(data) if (ref['doi'], ref['text']) not in completed}

        for future in tqdm(as_completed(future_to_ref), total=len(future_to_ref)):
            annotated_refs.append(future.result())

            with open(args.output, "w") as f:
                json.dump(annotated_refs, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Annotate references with the OpenAlex API.')

    parser.add_argument("--data", type=str, help="Path to the JSON file containing the references.", default="data/refs.json")
    parser.add_argument("--output", type=str, help="Path to the output JSON file.", default="out/openalex.json")

    args = parser.parse_args()
    main(args)
