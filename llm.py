"""
File: llm.py
------------

Annotates the references with a large language model.
"""
import json
import openai
from dotenv import load_dotenv
import argparse
from tqdm import tqdm

load_dotenv()
client = openai.Client()

TRAINING_REF = {
  "doi": "10.12688%2Fopenreseurope.15810.2",
  "elt_text": "<mixed-citation publication-type=\"journal\">\n                    <person-group person-group-type=\"author\">\n\n                        <name name-style=\"western\">\n                            <surname>Krug</surname>\n                            <given-names>K</given-names>\n                        </name>\n\n                        <name name-style=\"western\">\n                            <surname>Jaehnig</surname>\n                            <given-names>EJ</given-names>\n                        </name>\n\n                        <name name-style=\"western\">\n                            <surname>Satpathy</surname>\n                            <given-names>S</given-names>\n                        </name>\n\n                        <etal />\n               </person-group>:\n                    <article-title>Proteogenomic Landscape of Breast Cancer Tumorigenesis and Targeted Therapy.</article-title>\n                    <source>\n\n                        <italic toggle=\"yes\">Cell.</italic>\n               </source>\n               <year>2020</year>;<volume>183</volume>(<issue>5</issue>):<fpage>1436</fpage>&#8211;<lpage>1456</lpage>.\n                    <elocation-id>e31</elocation-id>.\n                    <pub-id pub-id-type=\"pmid\">33212010</pub-id>\n                    <pub-id pub-id-type=\"doi\">10.1016/j.cell.2020.10.036</pub-id>\n                    <pub-id pub-id-type=\"pmcid\">8077737</pub-id>\n                </mixed-citation>",
  "text": "Krug K    Jaehnig EJ    Satpathy S    : Proteogenomic Landscape of Breast Cancer Tumorigenesis and Targeted Therapy.   Cell.  2020;183(5):1436\u20131456. e31. 33212010 10.1016/j.cell.2020.10.036 8077737"
}


def prompt(ref):
    return [
        {"role": "system", "content": "You are an expert in annotating references using the Journal Article Tag Suite (JATS). Respond only with the annotated references in JATS format and nothing else."},
        {"role": "user", "content": f"Annotate this reference in JATS format:\n\n{TRAINING_REF['text']}"},
        {"role": "assistant", "content": f"```xml\n{TRAINING_REF['elt_text']}\n```"},
        {"role": "user", "content": f"Annotate this reference in JATS format:\n\n{ref['text']}"}
    ]

def main(args):
    data = json.load(open(args.data))

    # exclude the training reference
    data = [ref for ref in data if (ref['doi'], ref['text']) != (TRAINING_REF['doi'], TRAINING_REF['text'])]

    # get the completed annotations
    try:
        annotated_refs = json.load(open(args.output))
    except FileNotFoundError:
        completed = set()
    else:
        completed = set((ref['doi'], ref['text']) for ref in annotated_refs)

    annotated_refs = []
    for ref in tqdm(data):
        if (ref['doi'], ref['text']) in completed:
            continue

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=prompt(ref),
            temperature=0.1
        )

        annotated_refs.append({
            "doi": ref['doi'],
            "text": ref['text'],
            "elt_text": ref['elt_text'],
            "prediction": response.choices[0].message.content
        })

        with open(args.output, "w") as f:
            json.dump(annotated_refs, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Annotate references with a large language model.')

    parser.add_argument("--data", type=str, help="Path to the JSON file containing the references.", default="data/refs.json")
    parser.add_argument("--output", type=str, help="Path to the output JSON file.", default="out/llm.json")

    args = parser.parse_args()
    main(args)
