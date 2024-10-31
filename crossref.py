"""
File: crossref.py
-----------------

Annotates the references with the Crossref API.
"""
import json
import requests
from dotenv import load_dotenv
import argparse
from tqdm import tqdm
import xml.etree.ElementTree as ET

TRAINING_REF = {
  "doi": "10.12688%2Fopenreseurope.15810.2",
  "elt_text": "<mixed-citation publication-type=\"journal\">\n                    <person-group person-group-type=\"author\">\n\n                        <name name-style=\"western\">\n                            <surname>Krug</surname>\n                            <given-names>K</given-names>\n                        </name>\n\n                        <name name-style=\"western\">\n                            <surname>Jaehnig</surname>\n                            <given-names>EJ</given-names>\n                        </name>\n\n                        <name name-style=\"western\">\n                            <surname>Satpathy</surname>\n                            <given-names>S</given-names>\n                        </name>\n\n                        <etal />\n               </person-group>:\n                    <article-title>Proteogenomic Landscape of Breast Cancer Tumorigenesis and Targeted Therapy.</article-title>\n                    <source>\n\n                        <italic toggle=\"yes\">Cell.</italic>\n               </source>\n               <year>2020</year>;<volume>183</volume>(<issue>5</issue>):<fpage>1436</fpage>&#8211;<lpage>1456</lpage>.\n                    <elocation-id>e31</elocation-id>.\n                    <pub-id pub-id-type=\"pmid\">33212010</pub-id>\n                    <pub-id pub-id-type=\"doi\">10.1016/j.cell.2020.10.036</pub-id>\n                    <pub-id pub-id-type=\"pmcid\">8077737</pub-id>\n                </mixed-citation>",
  "text": "Krug K    Jaehnig EJ    Satpathy S    : Proteogenomic Landscape of Breast Cancer Tumorigenesis and Targeted Therapy.   Cell.  2020;183(5):1436\u20131456. e31. 33212010 10.1016/j.cell.2020.10.036 8077737"
}

def crossref_to_mixed_citation(api):
    # Register the xlink namespace
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

    # Get the first item from the Crossref API response
    item = api['message']['items'][0]
    mixed_citation = ET.Element('mixed-citation')

    # Extract and include the tags if they exist

    # Year
    year = None
    if 'published-print' in item and 'date-parts' in item['published-print']:
        year = item['published-print']['date-parts'][0][0]
    elif 'published-online' in item and 'date-parts' in item['published-online']:
        year = item['published-online']['date-parts'][0][0]
    elif 'issued' in item and 'date-parts' in item['issued']:
        year = item['issued']['date-parts'][0][0]
    if year:
        year_elem = ET.SubElement(mixed_citation, 'year')
        year_elem.text = str(year)

    # Volume
    if 'volume' in item:
        volume = item['volume']
        volume_elem = ET.SubElement(mixed_citation, 'volume')
        volume_elem.text = volume

    # Issue
    issue = None
    if 'issue' in item:
        issue = item['issue']
    elif 'journal-issue' in item and 'issue' in item['journal-issue']:
        issue = item['journal-issue']['issue']
    if issue:
        issue_elem = ET.SubElement(mixed_citation, 'issue')
        issue_elem.text = issue

    # Fpage and Lpage (pages)
    if 'page' in item:
        pages = item['page']
        if '-' in pages:
            fpage, lpage = pages.split('-', 1)
            fpage_elem = ET.SubElement(mixed_citation, 'fpage')
            fpage_elem.text = fpage
            lpage_elem = ET.SubElement(mixed_citation, 'lpage')
            lpage_elem.text = lpage
        else:
            fpage_elem = ET.SubElement(mixed_citation, 'fpage')
            fpage_elem.text = pages

    # Source (journal title)
    if 'container-title' in item and item['container-title']:
        source = item['container-title'][0]
        source_elem = ET.SubElement(mixed_citation, 'source')
        source_elem.text = source

    # Article title
    if 'title' in item and item['title']:
        article_title = item['title'][0]
        article_title_elem = ET.SubElement(mixed_citation, 'article-title')
        article_title_elem.text = article_title

    # Authors
    if 'author' in item and item['author']:
        person_group_elem = ET.SubElement(mixed_citation, 'person-group')
        for author in item['author']:
            given = author.get('given', '')
            family = author.get('family', '')
            suffix = author.get('suffix', '')
            name_parts = [given, family]
            name = ' '.join(filter(None, name_parts))
            name_elem = ET.SubElement(person_group_elem, 'name')
            name_elem.text = name
            if suffix:
                suffix_elem = ET.SubElement(name_elem, 'suffix')
                suffix_elem.text = suffix

    # collab (collaborators)
    if 'collaborator' in item:
        collab = item['collaborator']
        collab_elem = ET.SubElement(mixed_citation, 'collab')
        collab_elem.text = collab

    # pub-id (e.g., DOI)
    if 'DOI' in item:
        doi = item['DOI']
        pub_id_elem = ET.SubElement(mixed_citation, 'pub-id', {'pub-id-type': 'doi'})
        pub_id_elem.text = doi

    # ext-link (e.g., URL)
    if 'URL' in item:
        url = item['URL']
        ext_link_elem = ET.SubElement(mixed_citation, 'ext-link', {
            'ext-link-type': 'uri',
            '{http://www.w3.org/1999/xlink}href': url
        })
        ext_link_elem.text = url

    # Generate the XML string
    xml_string = ET.tostring(mixed_citation, encoding='unicode')

    return xml_string

def main(args):
    data = json.load(open(args.data))

    # exclude the training reference
    data = [ref for ref in data if (ref['doi'], ref['text']) != (TRAINING_REF['doi'], TRAINING_REF['text'])]

    # get the completed annotations
    try:
        annotated_refs = json.load(open(args.output))
    except FileNotFoundError:
        annotated_refs = []
        completed = set()
    else:
        completed = set((ref['doi'], ref['text']) for ref in annotated_refs)

    for ref in tqdm(data):
        if (ref['doi'], ref['text']) in completed:
            continue

        response = requests.get(f'http://api.crossref.org/works?query.bibliographic="{ref["text"]}"&rows=2')
        response = response.json()

        try:
            items = response['message']['items']
        except Exception:
            annotated_refs.append({
                "doi": ref['doi'],
                "text": ref['text'],
                "elt_text": ref['elt_text'],
                "prediction": f"<mixed-citation></mixed-citation>"
            })
            continue

        if not items:
            annotated_refs.append({
                "doi": ref['doi'],
                "text": ref['text'],
                "elt_text": ref['elt_text'],
                "prediction": f"<mixed-citation></mixed-citation>"
            })
            continue

        if args.confident:
            if items[0]['score'] < 50:
                annotated_refs.append({
                    "doi": ref['doi'],
                    "text": ref['text'],
                    "elt_text": ref['elt_text'],
                    "prediction": f"<mixed-citation></mixed-citation>"
                })
                continue

        if args.conclusive:
            try:
                scores = items[0]['score'], items[1]['score']

                # if the scores are within 5 points of each other it's inconclusive
                if abs(scores[0] - scores[1]) < 5:
                    annotated_refs.append({
                        "doi": ref['doi'],
                        "text": ref['text'],
                        "elt_text": ref['elt_text'],
                        "prediction": f"<mixed-citation></mixed-citation>"
                    })
                    continue
            except IndexError:
                pass


        annotated_refs.append({
            "doi": ref['doi'],
            "text": ref['text'],
            "elt_text": ref['elt_text'],
            "prediction": crossref_to_mixed_citation(response)
        })

        with open(args.output, "w") as f:
            json.dump(annotated_refs, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Annotate references with the Crossref API.')

    parser.add_argument("--data", type=str, help="Path to the JSON file containing the references.", default="data/refs.json")
    parser.add_argument("--output", type=str, help="Path to the output JSON file.", default="out/crossref.json")
    parser.add_argument("--confident", action="store_true", help="Only annotate references with a high confidence score.", default=False)
    parser.add_argument("--conclusive", action="store_true", help="Only annotate references that are conclusive.", default=False)

    args = parser.parse_args()
    main(args)
