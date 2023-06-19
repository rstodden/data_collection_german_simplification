# Data Collection for a German Text Simplification and Text Leveling Corpus
This repository contains code for a web crawler to download parallel texts in standard German and plain or easy-to-understand German. For each source, we aimed at downloading the
complete relevant content of the websites. We removed parts such as navigation, advertisement, contact data, and other unnecessary stuff.
For some web pages, the documents for which no parallel document could be found are also downloaded. 

Furthermore, the web crawler recognizes paragraph endings and save the text also including a paragraph marker "SEPL|||SEPR" (see text_par directories).  
The resulting parallel documents can be used for document-level simplification. 
The documents can be also split into sentences (see sentence_split.py) and label their complexity level, which facilitate a usage for text leveling, too.

The current list of supported web pages can be found in the table below.

The data folder contains a preview of the full corpus. 
Please check the copyright of each website yourself, to make sure you are allowed to use it (the copyright for academic or industry purpose might be different). 

The parallel documents can be also uploaded in the text simplification annotation tool TS-ANNO ([Stodden, Kallmeyer (2022)](https://github.com/rstodden/TS_annotation_tool)) for further annotation, e.g., sentence-wise alignment. 
The output format of this code is identical to the input format of TS-ANNO.

The web crawler was already used to download the data for the DEplain-web corpus. See [Stodden et. al., 2023](https://github.com/rstodden/DEPlain) for more information regarding the corpus and the web harvester.




| website                                                                                                                         | simple level | complex level | domain           | copyright | status   |
|---------------------------------------------------------------------------------------------------------------------------------|--------------|---------------|------------------|--------|----------|
| https://www.alumniportal-deutschland.org/services/sitemap/                                                                      | A2           | B2            | language learner |  | &#9940;  |
| https://www.apotheken-umschau.de/einfache-sprache/     ‡                                                                          | B1           | C2            | biomed           | x | &#9989; |
| https://www.bpb.de/nachschlagen/lexika/lexikon-in-einfacher-sprache/                                                            | A2/B1        | C2            | politics         | x | &#9680;|
| https://www.bpb.de/nachschlagen/lexika/das-junge-politik-lexikon/                                                               | children_6   | C2            | politics         | x | &#9680; |
| https://www.bzfe.de/einfache-sprache/                                                                                           | A2/B1        | C2            | health/food      | x | &#9989; |
| https://www.einfach-teilhaben.de/DE/LS/Home/leichtesprache_node.html                                                            | A1           | C2            | web              | x | &#9989; |
| https://einfachebuecher.de/                                                                                                     | A2/B1        | C2            | fiction          | x | &#9989; |
| https://www.hamburg.de/hamburg-barrierefrei/leichte-sprache/                                                                    | A1           | C2            | web              | x | &#9989; |
| https://www.lebenshilfe-main-taunus.de/inhalt/                                                                                  | A1           | C2            | accessibility    | x | &#9989; |
| https://offene-bibel.de/  ‡                                                                                                      | A1           | C2            | bible            | x | &#9989; |
| https://www.passanten-verlag.de/                                                                                                | A2/B1        | C2            | fiction          | x | &#9989; |
| https://www.stadt-koeln.de/leben-in-koeln/soziales/informationen-leichter-sprache                                               | A1           | C2            | web              | x | &#9989; |
| https://www.evangelium-in-leichter-sprache.de/bibelstellen                                                                      | A1           | C2            | bible            | x | &#11036; |
| https://www.ndr.de/fernsehen/barrierefreie_angebote/leichte_sprache/Maerchen-in-Leichter-Sprache,maerchenleichtesprache100.html ‡ | A1 | C2 | fiction          | x | &#9989; |
| https://www.nachrichtenleicht.de/                                                                                               | A1 |  | news             | x | &#11036; |
| https://hurraki.de/wiki/Hauptseite                                                                                              | A1 | | wiki             | x | &#11036; |
| party programs                                                                                                                  | A1 | | politics         | x | &#11036; |
| instructions citizen participation                                                                                              | A1 | | politics         | x | &#11036; |
| https://www.monheim.de/footer/leichte-sprache/inhalts-uebersicht | A1 | C2 | web |x | &#11036; |

: This table summarizes the web pages (including metadata) which can be extracted with the web crawler. The data provider of the documents marked with ‡ explicitely state that their
documents are professionally simplified and reviewed by the target group.


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

## Document Alignment
The documents are aligned with three strategies in the following order: 
1) automatic alignment by the reference to the simple document within the complex documents, 
2) automatically matching the titles of the documents on the website, and 
3) aligning the documents manually (see [links/](https://github.com/rstodden/data_collection_german_simplification/tree/master/links)). 

All the books in the fiction domain were manually aligned on the document level as the complex data is provided on another web page (i.e. [Projekt Gutenberg](https://www.projekt-gutenberg.org/)) than the simplified data (i.e., [Spaß am Lesen Verlag](https://einfachebuecher.de/), [Passanten Verlag](https://www.passanten-verlag.de/), or [NDR](https://www.ndr.de/fernsehen/barrierefreie_angebote/leichte_sprache/Maerchen-in-Leichter-Sprache,maerchenleichtesprache100.html)).

## Warning
Web content can change very frquently, so maybe the web crawler does not suport all web pages named above anymore. Some web pages might have meanwhile changed their URLs or the HTML structure. In main function of [get_urls_list.py](https://github.com/rstodden/data_collection_german_simplification/blob/master/get_urls_list.py#L833) you can disable web pages for which the crawler currently does not work (or web pages you are not interested in). We plan to overcome this issue in future by providing links to archived versions of the web pages.

## Contributions
Feel free to add more webpages or add code to crawl the webpages. 

## License
This code is licensed under [GPL-3.0 license](LICENSE).

## Citation
If you use part of this work, please cite our paper:

```
@inproceedings{stodden-etal-2023-deplain,
    title = "{DE}-plain: A German Parallel Corpus with Intralingual Translations into Plain Language for Sentence and Document Simplification",
    author = "Stodden, Regina  and
      Momen, Omar  and
      Kallmeyer, Laura",
    booktitle = "Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics",
    month = jul,
    year = "2023",
    address = "Toronto, Canada",
    publisher = "Association for Computational Linguistics",
    notes = "preprint: https://arxiv.org/abs/2305.18939",
}

```
