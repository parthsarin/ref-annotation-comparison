# Reference Annotation Comparison

Comparing reference annotation accuracy for four different services:

- [Crossref API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
- [Google Scholar API](https://github.com/scholarly-python-package/scholarly)
- Language Model
- Gazzi-style DOI extraction

## Data

The data are JATS files sampled from the [Open Research Europe](https://open-research-europe.ec.europa.eu/) publishing platform. They're stored in the `data` directory and the `flatten_refs.py` file extracts the references from each of those files and stores the text version and the JATS annotated version in the `data` directory.

There are a total of 3,588 unique references in the data. We used 3587 for evaluation and one (shown below) for one-shot learning.

## LLM Annotation

We used one-shot annotation from GPT-4o mini to produce the reference annotation, with the following sample as the "training" data:

```json
{
  "doi": "10.12688%2Fopenreseurope.15810.2",
  "elt_text": "<mixed-citation publication-type=\"journal\">\n                    <person-group person-group-type=\"author\">\n\n                        <name name-style=\"western\">\n                            <surname>Krug</surname>\n                            <given-names>K</given-names>\n                        </name>\n\n                        <name name-style=\"western\">\n                            <surname>Jaehnig</surname>\n                            <given-names>EJ</given-names>\n                        </name>\n\n                        <name name-style=\"western\">\n                            <surname>Satpathy</surname>\n                            <given-names>S</given-names>\n                        </name>\n\n                        <etal />\n               </person-group>:\n                    <article-title>Proteogenomic Landscape of Breast Cancer Tumorigenesis and Targeted Therapy.</article-title>\n                    <source>\n\n                        <italic toggle=\"yes\">Cell.</italic>\n               </source>\n               <year>2020</year>;<volume>183</volume>(<issue>5</issue>):<fpage>1436</fpage>&#8211;<lpage>1456</lpage>.\n                    <elocation-id>e31</elocation-id>.\n                    <pub-id pub-id-type=\"pmid\">33212010</pub-id>\n                    <pub-id pub-id-type=\"doi\">10.1016/j.cell.2020.10.036</pub-id>\n                    <pub-id pub-id-type=\"pmcid\">8077737</pub-id>\n                </mixed-citation>",
  "text": "Krug K    Jaehnig EJ    Satpathy S    : Proteogenomic Landscape of Breast Cancer Tumorigenesis and Targeted Therapy.   Cell.  2020;183(5):1436\u20131456. e31. 33212010 10.1016/j.cell.2020.10.036 8077737"
}
```

Consequently, this sample is excluded from the evaluation. We chose this sample because it contains a complex JATS structure (e.g. 10 unique sub-elements of the `<mixed-citation>` tag).

## Evaluation

This table shows statistics for annotation using different APIs on the entire (3,587) dataset:

|                    | Coverage | Title Match | Avg Cost / Ref | Duration |
| ------------------ | -------- | ----------- | -------------- | -------- |
| Crossref API       | 96.8%    | 42.47%      | $0.00          | 1h       |
| Google Scholar API |          |             |                |          |
| Language Model     | 100%     | 85.6%       | $0.003         | 4h       |
| DOI Search         |          |             |                |          |
