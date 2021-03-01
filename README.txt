# Data Collection for  a German Text Simplification Corpus

## Pipeline
1) pip install -r requirements.txt
2) python get_urls_list.py
Reminder:
Do not use the code of Battisti, because not allowed to distribute. Reimplement with same structure for files according to their paper.

Corpus Size:
- TAZ: 48 simpl documents, 37 parallel documents
- Apotheken Umschau: 43 parallel documents
- Hamburg.de: 56 parallel documents
- stadt-koeln.de: 93 parallel documents
- Spaß am Lesen / Gutenberg: 14 parallel extracts of documents
- Basic Law of Germany: 19 parallel laws in different versions https://www.leichte-sprache.org/wp-content/uploads/2018/01/Grund-Rechte-LS-Web-Version_16-06-15_barrierefrei-1.pdf complex https://www.btg-bestellservice.de/pdf/10060000.pdf
- Fairytales: 12 parallel fairytales of the Brothers Grimm
- party programm: 11 parallel. 6 Bundestagswahl 2017 (CDU, SPD, Grüne, Linke, FDP 2x), 5 Europawahl 2019 (HTML Kurzfassung + PDF Langfassung)
- Definitions of terms: @todo: find an full sentence definition dataset for German words. First Paragraph of Wikipedia? For simplified language use: https://www.bpb.de/nachschlagen/lexika/lexikon-in-einfacher-sprache/ https://www.lebenshilfe.de/woerterbuch/?tx_lfdictionary_list%5Boffset%5D=0&cHash=f4fbc8254f25d19f9cc5243755281650 https://hurraki.de/wiki/Hurraki:Artikel_von_A_bis_Z
- News: @todo
	# https://www.sr.de/sr/home/nachrichten/nachrichten_einfach/index.html
	# http://www.einfach-informiert.at/
	# https://kurier.at/einfache-sprache
	# https://www.ndr.de/fernsehen/service/leichte_sprache/Alle-Nachrichten-in-Leichter-Sprache,leichtesprachearchiv110.html
	# https://www.mdr.de/nachrichten-leicht/rueckblick/leichte-sprache-rueckblick-buendelgruppe-sachsen-100.html
	# https://www.mdr.de/nachrichten-leicht/rueckblick/leichte-sprache-rueckblick-buendelgruppe-sachsen-anhalt-100.html
	# https://www.mdr.de/nachrichten-leicht/rueckblick/leichte-sprache-rueckblick-buendelgruppe-thueringen-100.html
	# https://www.mdr.de/nachrichten-leicht/index.html
	# !!! https://science.apa.at/site/home/kooperation.html?marsname=/Lines/Science/Koop/topeasy [used in Battisti etal (2020) and in Säuberli etal (2020)
	# https://www.nachrichtenleicht.de/
	# https://www.zdf.de/kinder/logo
	#
- Bible: 174. CC BY-SA 3.0  129 in working progress , 35 waiting for proof , 10 verified. Alltagssprache use Studienfassung only text and not text of spans. (https://offene-bibel.de/wiki/Kapitelliste)
    https://www.evangelium-in-leichter-sprache.de/bibelstellen
- 161 DaF texts https://www.alumniportal-deutschland.org/services/sitemap/ li Deutsch auf die Schnelle -> ul. Texte in B2 und A2 + Verständnisfragen
Compared to Klaper.
- https://www.einfach-teilhaben.de/: 69 parallel documents (+ more text on subpages not considered so far)
- https://www.gww-netz.de/de-LS/ Still same content, but restructured. try to consider same path on both sites
- Heilpädagogische Hilfe Osnabrück: 79 parallel documents. In comparison to Klaper, restructured. But parallel documents linked!
- Lebenshilfe main Taunus: 86 parallel documents.
- OWB only in LS. no texts only listings.

- https://www.bnw-opfingen.de/kurz-einfach.html https://www.bnw-opfingen.de/
- https://www.bankaustria.at/barrierefrei/index.jsp

==> 37 + 43 + 56 + 93 + 14 + 19 + 12 + 11 + 174 + 69 + 86 +79 + 161 = 854

@ TODO:
- SEARCH FOR LEICHTER LESEN in AT
- contact each website if it is fine for them to use and publish their data. if not, just publish the code.
- http://rechtleicht.at/
- http://www.ich-kenne-meine-rechte.de/index.php?%20menuid=1
- https://www.bundesregierung.de/breg-de/leichte-sprache?view=
- https://www.gemeinsam-einfach-machen.de/GEM/DE/Service/Inhalt/inhalt_node.html
- http://vzopc4.gbv.de:8080/DB=22/CMD?ACT=SRCHA&IKT=5040&SRT=YOP&TRM=Leichte+Sprache
- http://www.on-line-on.eu/inhalt.php
- more books https://www.leichte-sprache.org/geschichten/
- check this referencelist http://www.leicht-gesagt.de/agentur-leichte-sprache-referenzen.html
- https://www.bundestag.de/leichte_sprache/was_macht_der_bundestag/parlament    https://www.das-parlament.de/2020

# Workflow
- find all parallel documents with `get_urls_list.py`
- save plain text of parallel documents with `extract_text_data.py`