# Data Collection for a German Text Simplification and Text Leveling Corpus
This repository contains code for a web crawler to download parallel texts in standard German and plain or easy-to-understand German.
For some web pages, the documents for which no parallel document could be found are also downloaded. 

Furthermore, the web crawler recognizes paragraph endings and save the text also including a paragraph marker "SEPL|||SEPR" (see text_par directories).  
The resulting parallel documents can be used for document-level simplification. 
The documents can be also split into sentences (see sentence_split.py) and label their complexity level, which facilitate a usage for text leveling, too.

The current list of supported web pages can be found in the table below.

The data folder contains a preview of the full corpus. 
Please check the copyright of each website yourself, to make sure you are allowed to use it (the copyright for academic or industry purpose might be different). 

The parallel documents can be also uploaded in the text simplification annotation tool TS-ANNO ([Stodden, Kallmeyer (2022)](https://github.com/rstodden/TS_annotation_tool)) for further annotation, e.g., sentence-wise alignment. 
The output format of this code is identical to the input format of TS-ANNO.

| website                                                                                                                         | simple level | complex level | domain           | copyright | status   |
|---------------------------------------------------------------------------------------------------------------------------------|--------------|---------------|------------------|--------|----------|
| https://www.alumniportal-deutschland.org/services/sitemap/                                                                      | A2           | B2            | language learner |  | &#9940;  |
| https://www.apotheken-umschau.de/einfache-sprache/                                                                              | B1           | C2            | biomed           | x | &#9989; |
| https://www.bpb.de/nachschlagen/lexika/lexikon-in-einfacher-sprache/                                                            | A2/B1        | C2            | politics         | x | &#9989; |
| https://www.bpb.de/nachschlagen/lexika/das-junge-politik-lexikon/                                                               | children_6   | C2            | politics         | x | &#9989; |
| https://www.bzfe.de/einfache-sprache/                                                                                           | A2/B1        | C2            | health/food      | x | &#9989; |
| https://www.einfach-teilhaben.de/DE/LS/Home/leichtesprache_node.html                                                            | A1           | C2            | web              | x | &#9989; |
| https://einfachebuecher.de/                                                                                                     | A2/B1        | C2            | fiction          | x | &#9989; |
| https://www.hamburg.de/hamburg-barrierefrei/leichte-sprache/                                                                    | A1           | C2            | web              | x | &#9989; |
| https://www.lebenshilfe-main-taunus.de/inhalt/                                                                                  | A1           | C2            | accessibility    | x | &#9989; |
| https://offene-bibel.de/                                                                                                        | A1           | C2            | bible            | x | &#9989; |
| https://www.passanten-verlag.de/                                                                                                | A2/B1        | C2            | fiction          | x | &#9989; |
| https://www.stadt-koeln.de/leben-in-koeln/soziales/informationen-leichter-sprache                                               | A1           | C2            | web              | x | &#9989; |
| https://www.evangelium-in-leichter-sprache.de/bibelstellen                                                                      | A1           | C2            | bible            | x | &#11036; |
| https://www.ndr.de/fernsehen/barrierefreie_angebote/leichte_sprache/Maerchen-in-Leichter-Sprache,maerchenleichtesprache100.html | A1 | C2 | fiction          | x | &#9989; |
| https://www.nachrichtenleicht.de/                                                                                               | A1 |  | news             | x | &#11036; |
| https://hurraki.de/wiki/Hauptseite                                                                                              | A1 | | wiki             | x | &#11036; |
| party programs                                                                                                                  | A1 | | politics         | x | &#11036; |
| instructions citizen participation                                                                                              | A1 | | politics         | x | &#11036; |
| https://www.monheim.de/footer/leichte-sprache/inhalts-uebersicht | A1 | C2 | web |x | &#11036; |

## Installation
1) Please install Python 3.
2) Get your own copy of the code with git clone.
3) Install required packages (see requirements.txt)

## Usage
### Download Parallel Documents
1)  ``python get_urls_list.py``: get all urls of parallel documents and save the html content
2) ``python extract_text_data.py``: save plain text (and plain text with paragraph border "SEPL|||SEPR") of parallel documents

### Create Text Leveling Dataset 
1) ``python -m spacy download de_dep_news_trf`` download the NLP pipeline of spacy
2) ``python sentence_split.py``: split the sentences of the parallel documents (and simple only) into sentences and label them with their complexity level

## Data Format
Each plain text file, follows the same data format. Parallel simple and complex files are named with the same identifier (e.g., simple_111.txt and complex_111.txt). 
An overview of all parallel files and all meta data is provided in [url_overview.tsv] and [url_overview_text.tsv].
The first line of each parallel file contains meta data and the second line contains the plain text (without linebreaks).
The format of the meta data of the first line looks like this: 
``# © Origin: source_of_data [last accessed: YYYY-MM-DD]\ttitle_of_document` 


## Contributions
Feel free to add more webpages or add code to crawl the webpages. 

## License
This code is licensed under [todo] license.

## Citation
If you this code in your research, please cite
```
[todo]
```

## ToDo:
- make preview with 15%
- creaet table with all links plus status
