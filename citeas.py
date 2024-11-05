"""
File: citeas.py
---------------

Annotates the references with the CiteAs API.
"""
import json
import requests
import argparse
from tqdm import tqdm
import xml.etree.ElementTree as ET

TRAINING_REF = {
  "doi": "10.12688%2Fopenreseurope.15810.2",
  "elt_text": "<mixed-citation publication-type=\"journal\">\n                    <person-group person-group-type=\"author\">\n\n                        <name name-style=\"western\">\n                            <surname>Krug</surname>\n                            <given-names>K</given-names>\n                        </name>\n\n                        <name name-style=\"western\">\n                            <surname>Jaehnig</surname>\n                            <given-names>EJ</given-names>\n                        </name>\n\n                        <name name-style=\"western\">\n                            <surname>Satpathy</surname>\n                            <given-names>S</given-names>\n                        </name>\n\n                        <etal />\n               </person-group>:\n                    <article-title>Proteogenomic Landscape of Breast Cancer Tumorigenesis and Targeted Therapy.</article-title>\n                    <source>\n\n                        <italic toggle=\"yes\">Cell.</italic>\n               </source>\n               <year>2020</year>;<volume>183</volume>(<issue>5</issue>):<fpage>1436</fpage>&#8211;<lpage>1456</lpage>.\n                    <elocation-id>e31</elocation-id>.\n                    <pub-id pub-id-type=\"pmid\">33212010</pub-id>\n                    <pub-id pub-id-type=\"doi\">10.1016/j.cell.2020.10.036</pub-id>\n                    <pub-id pub-id-type=\"pmcid\">8077737</pub-id>\n                </mixed-citation>",
  "text": "Krug K    Jaehnig EJ    Satpathy S    : Proteogenomic Landscape of Breast Cancer Tumorigenesis and Targeted Therapy.   Cell.  2020;183(5):1436\u20131456. e31. 33212010 10.1016/j.cell.2020.10.036 8077737"
}


def citeas_to_mixed_citation(data):
    # Extract main elements
    article_title = ""
    journal_title = ""
    year = ""
    volume = ""
    issue = ""
    first_page = ""
    last_page = ""
    doi = ""

    # Parse data
    for assertion in data['metadata'].get('assertion', []):
        if assertion['name'] == 'articletitle':
            article_title = assertion['value']
        elif assertion['name'] == 'journaltitle':
            journal_title = assertion['value']

    year = data['metadata'].get('issued', {}).get('date-parts', [[None]])[0][0]
    volume = data['metadata'].get('volume', "")
    issue = data['metadata'].get('issue', "")
    first_page = data['metadata'].get('page', "").split('-')[0]
    last_page = data['metadata'].get('page', "").split('-')[-1].split('.')[0]  # Split if there is an elocation part
    doi = data['metadata'].get('DOI', "")
    article_title = data['metadata'].get('title', '')

    # Generate author list
    authors = data['metadata'].get('author', [])
    author_list = ""
    for author in authors:
        given_names = author['given'][0]  # First initial of the given name
        if len(author['given'].split()) > 1:
            given_names += author['given'].split()[1][0]  # Add middle initial if exists
        author_list += f"""
            <name name-style="western">
                <surname>{author['family']}</surname>
                <given-names>{given_names}</given-names>
            </name>"""
        if author['sequence'] == 'first':
            break  # Stop after the first author to keep the XML short with <etal />
    author_list += "\n<etal />"

    # Build the JATS XML
    jats_xml = f"""
    <mixed-citation publication-type="journal">
        <person-group person-group-type="author">
            {author_list}
        </person-group>:
        <article-title>{article_title}.</article-title>
        <source><italic toggle="yes">{journal_title}.</italic></source>
        <year>{year}</year>;<volume>{volume}</volume>(<issue>{issue}</issue>):<fpage>{first_page}</fpage>&#8211;<lpage>{last_page}</lpage>.
        <pub-id pub-id-type="doi">{doi}</pub-id>
    </mixed-citation>
    """.strip()

    return jats_xml

def get_reference(ref, idx):
    r = requests.get(f'https://api.citeas.org/product/{ref["text"]}?email=psarin@sfu.ca')

    try:
        prediction = citeas_to_mixed_citation(r.json())
    except Exception:
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
    except Exception:
        annotated_refs = []
        completed = set()

    for ref in tqdm(data):
        if (ref['doi'], ref['text']) in completed:
            continue

        result = get_reference(ref, 0)
        annotated_refs.append(result)

        with open(args.output, "w") as f:
            json.dump(annotated_refs, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Annotate references with the CiteAs API.')

    parser.add_argument("--data", type=str, help="Path to the JSON file containing the references.", default="data/refs.json")
    parser.add_argument("--output", type=str, help="Path to the output JSON file.", default="out/citeas.json")

    args = parser.parse_args()
    main(args)
