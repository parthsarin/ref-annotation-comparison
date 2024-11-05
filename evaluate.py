import json
import xml.etree.ElementTree as ET
import editdistance
from prettytable import PrettyTable, TableStyle

def test_matches(predictions, element='article-title', tol=5):
    elt_matches = 0
    total_articles = 0
    for ref in predictions:
        correct = ref['elt_text']
        prediction = ref['prediction'].strip('`xml')
        if prediction == "<mixed-citation></mixed-citation>":
            continue

        # parsing errors
        correct_xml = ET.fromstring(correct)
        try:
            prediction_xml = ET.fromstring(prediction)
        except ET.ParseError:
            continue

        # does the element occur (find the first)
        correct_elt = correct_xml.find(f'.//{element}')
        if correct_elt is None:
            continue
        else:
            correct_elt = correct_elt.text
            total_articles += 1

        # find the elt
        prediction_elt = prediction_xml.find(element)
        if prediction_elt is None:
            prediction_elt = prediction_xml.find('source')
        if prediction_elt is None:
            continue

        # is the elt empty?
        prediction_elt = prediction_elt.text
        if prediction_elt is None:
            continue

        # edit distance
        if editdistance.eval(correct_elt, prediction_elt) <= tol:
            elt_matches += 1

    return elt_matches / total_articles

table = PrettyTable()
table.field_names = [
    "",
    "Coverage",
    "`article-title` Match",
    "`fpage` Match",
    "`year` Match",
    "Avg Cost / Ref",
    "Duration"
]

FILES = [
    {'path': 'out/llm.json', 'name': 'Language Model', 'cost': '$0.003', 'duration': '4h'},
    {'path': 'out/crossref.json', 'name': 'Crossref API', 'cost': '$0.00', 'duration': '1h'},
    {'path': 'out/crossref_confident_conclusive.json', 'name': 'Crossref (confident, conclusive)', 'cost': '$0.00', 'duration': '1h'},
    {'path': 'out/anystyle.json', 'name': 'Anystyle', 'cost': '$0.00', 'duration': '4m'},
    {'path': 'out/openalex.json', 'name': "OpenAlex", 'cost': '$0.00', 'duration': '1h'},
    {'path': 'out/citeas.json', 'name': 'CiteAs', 'cost': '$0.00', 'duration': '4h'}
]

for file in FILES:
    predictions = json.load(open(file['path']))
    hits = len([ref for ref in predictions if ref['prediction'] != "<mixed-citation></mixed-citation>"])

    table.add_row([
        file['name'],
        f"{hits / len(predictions):.2%}",
        f"{test_matches(predictions, 'article-title'):.2%}",
        f"{test_matches(predictions, 'fpage', tol=0):.2%}",
        f"{test_matches(predictions, 'year', tol=0):.2%}",
        file['cost'],
        file['duration']
    ])

table.set_style(TableStyle.MARKDOWN)
table.align = "l"
print(table)
