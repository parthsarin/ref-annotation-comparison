# Reference Annotation Comparison

Comparing reference annotation accuracy for four different services:

- [Crossref](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
- [Anystyle](https://anystyle.io/)
- Language Model
- Gazzi-style DOI extraction
- [OpenAlex](https://openalex.org/)

Services to be tested:

- [Google Scholar API](https://github.com/scholarly-python-package/scholarly)
- [CiteAs](https://citeas.org/)
- [Semantic Scholar](https://www.semanticscholar.org/)
- [WikiData](https://www.wikidata.org/wiki/Wikidata:Main_Page)
- Other things mentioned on [this Crossref blog post](https://www.crossref.org/labs/resolving-citations-we-dont-need-no-stinkin-parser/)
- Other things mentioned on [this totally different Crossref blog post]

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

|                                  | Coverage | `article-title` Match | `fpage` Match | `year` Match | Avg Cost / Ref | Duration |
| :------------------------------- | :------- | :-------------------- | :------------ | :----------- | :------------- | :------- |
| Language Model                   | 100.00%  | 85.60%                | 92.12%        | 92.30%       | $0.003         | 4h       |
| Crossref                         | 96.82%   | 43.88%                | 77.04%        | 65.44%       | $0.00          | 1h       |
| Crossref (confident, conclusive) | 63.18%   | 63.27%                | 84.92%        | 84.63%       | $0.00          | 1h       |
| Anystyle                         | 100.00%  | 66.99%                | 0.00%         | 0.44%        | $0.00          | 4m       |
| OpenAlex                         | 11.35%   | 0.50%                 | 0.00%         | 11.11%       | $0.00          | 1h       |
| CiteAs                           | 8.35%    | 29.73%                | 51.85%        | 34.21%       | $0.00          | 4h       |
| DOI Extraction                   | 59.39%   |                       |               |              |                |          |
