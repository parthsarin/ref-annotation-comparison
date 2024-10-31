"""
File: anystyle.py
-----------------

Test the AnyStyle API.
"""
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

cookies = {
    '_any_style_session': '6FWf3x3qWkf%2Fje5VWBFxpiw75OZxXcDpu4zMQu%2BYbuoCO4yhnY0tsfnzXVMMJcomZ7G35RHPPhBP7a4M7xffzQcLM92fUI1gRbg3fnz53nzy7ISD0SZnlQJVf02JD9nfWTVnbkC3tmDs5o6kUohaA2p6HvNzmLyGjI6I5OGRK0U9U8Kx2bPL6cskKvAFfq41AQI2PR13yu%2B2auHfcxABbnMx7B0XU3T731dWW%2BGYXxJdfGlcgqLaRKfRKScn8sOc80YqbAiA8JM3iJmE9WGhSYVxJdDLigz6iQw%3D--X7iqQntYHdj1JUKh--XNq7MqhtJRVp7oRQIsy4SQ%3D%3D',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:131.0) Gecko/20100101 Firefox/131.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://anystyle.io/',
    'X-CSRF-TOKEN': 'WQcgXYyEBbl6geZHb4Hc2aIvP6bZZDoOELBP0xw8eN2HXlhVvSZRAwkqImwtuu7Cdj9czDNG2RKDQykUjwmbaw==',
    'Content-Type': 'application/json;charset=utf-8',
    'Origin': 'https://anystyle.io',
    'Connection': 'keep-alive',
    # 'Cookie': '_any_style_session=6FWf3x3qWkf%2Fje5VWBFxpiw75OZxXcDpu4zMQu%2BYbuoCO4yhnY0tsfnzXVMMJcomZ7G35RHPPhBP7a4M7xffzQcLM92fUI1gRbg3fnz53nzy7ISD0SZnlQJVf02JD9nfWTVnbkC3tmDs5o6kUohaA2p6HvNzmLyGjI6I5OGRK0U9U8Kx2bPL6cskKvAFfq41AQI2PR13yu%2B2auHfcxABbnMx7B0XU3T731dWW%2BGYXxJdfGlcgqLaRKfRKScn8sOc80YqbAiA8JM3iJmE9WGhSYVxJdDLigz6iQw%3D--X7iqQntYHdj1JUKh--XNq7MqhtJRVp7oRQIsy4SQ%3D%3D',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Priority': 'u=0',
}

params = {
    'format': 'xml',
}

def convert_to_jats(sequence):
    citation = ET.Element('mixed-citation')
    publication_type = 'journal' if sequence.find('journal') is not None else 'reference'
    citation.set('publication-type', publication_type)

    # Author parsing
    author = sequence.find('author')
    if author is not None:
        person_group = ET.SubElement(citation, 'person-group')
        person_group.set('person-group-type', 'author')
        for name in author.text.split(','):
            name = name.strip()
            if name:
                name_element = ET.SubElement(person_group, 'name')
                name_element.set('name-style', 'western')
                surname, given_names = name.split()[0], ' '.join(name.split()[1:])
                surname_element = ET.SubElement(name_element, 'surname')
                surname_element.text = surname
                given_names_element = ET.SubElement(name_element, 'given-names')
                given_names_element.text = given_names

    # Title parsing
    title = sequence.find('title')
    if title is not None:
        article_title = ET.SubElement(citation, 'article-title')
        article_title.text = title.text.strip()

    # Journal parsing
    journal = sequence.find('journal')
    if journal is not None:
        source = ET.SubElement(citation, 'source')
        source.text = journal.text.strip()

    # Year parsing
    date = sequence.find('date')
    if date is not None:
        year = ET.SubElement(citation, 'year')
        year.text = date.text.strip().replace(';', '')

    # Volume parsing
    volume = sequence.find('volume')
    if volume is not None:
        vol_element = ET.SubElement(citation, 'volume')
        vol_element.text = volume.text.split(';')[0]

    # Pages parsing
    pages = sequence.find('pages')
    if pages is not None:
        page_parts = pages.text.split()
        if len(page_parts) > 2:
            pub_id = ET.SubElement(citation, 'pub-id')
            pub_id.set('pub-id-type', 'pmid')
            pub_id.text = page_parts[0]
            doi = ET.SubElement(citation, 'pub-id')
            doi.set('pub-id-type', 'doi')
            doi.text = page_parts[1]
            pmcid = ET.SubElement(citation, 'pub-id')
            pmcid.set('pub-id-type', 'pmcid')
            pmcid.text = page_parts[2]

    return citation

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

    to_do = [ref for ref in data if (ref['doi'], ref['text']) not in completed]
    batched_todo = [to_do[i:i + args.batch_size] for i in range(0, len(to_do), args.batch_size)]

    for batch in tqdm(batched_todo):
        ref_text = [ref["text"] for ref in batch]
        response = requests.post('https://anystyle.io/parse', params=params, cookies=cookies, headers=headers, json={'input': ref_text})

        response.raise_for_status()

        root = ET.fromstring(response.text)
        for ref, ref_xml in zip(batch, root.findall('sequence')):
            ref['prediction'] = ET.tostring(convert_to_jats(ref_xml), encoding='unicode')
            ref['raw_prediction'] = ET.tostring(ref_xml, encoding='unicode')
            annotated_refs.append(ref)

        with open(args.output, "w") as f:
            json.dump(annotated_refs, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Annotate references with the Crossref API.')

    parser.add_argument("--data", type=str, help="Path to the JSON file containing the references.", default="data/refs.json")
    parser.add_argument("--output", type=str, help="Path to the output JSON file.", default="out/anystyle.json")
    parser.add_argument("--batch-size", type=int, help="Number of references to annotate at once.", default=20)

    args = parser.parse_args()
    main(args)
