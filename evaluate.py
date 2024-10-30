import json
import xml.etree.ElementTree as ET
import editdistance

def test_matches(predictions):
    title_matches = 0
    total_articles = 0
    for ref in predictions:
        correct = ref['elt_text']
        prediction = ref['prediction'].strip('`xml')

        # parsing errors
        correct_xml = ET.fromstring(correct)
        try:
            prediction_xml = ET.fromstring(prediction)
        except ET.ParseError:
            continue

        # is there a title?
        correct_title = correct_xml.find('article-title')
        if correct_title is None:
            continue
        else:
            correct_title = correct_title.text
            total_articles += 1

        # find the title
        prediction_title = prediction_xml.find('article-title')
        if prediction_title is None:
            prediction_title = prediction_xml.find('source')
        if prediction_title is None:
            continue

        # is the title empty?
        prediction_title = prediction_title.text
        if prediction_title is None:
            continue

        # edit distance
        if editdistance.eval(correct_title, prediction_title) <= 5:
            title_matches += 1

    return title_matches / total_articles

print(f"Title matches for LLM: {test_matches(json.load(open('out/llm.json'))):.2%}")
print(f"Title matches for Crossref: {test_matches(json.load(open('out/crossref.json'))):.2%}")

crossref = json.load(open("out/crossref.json"))
crossref_hits = len([ref for ref in crossref if ref['prediction'] != "<mixed-citation></mixed-citation>"])
print(f"Crossref coverage: {crossref_hits / len(crossref):.2%}")
