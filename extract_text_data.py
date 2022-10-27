import os, re, csv, requests
from pathlib import Path
import bs4
import urllib.request
from datetime import datetime
import pandas as pd
# import stanza
# from spacy_stanza import StanzaLanguage
import xml.etree.ElementTree as ET
import re
import fitz


# docs, n_sents, n_token = 0, 0, 0

def filter_and_extract_data(dataframe, filter=None):
	if filter:
		column, value = filter
		dataframe = dataframe.loc[dataframe[column] == value]

	output_frame = iterate_files(dataframe)
	return output_frame



def html2soup(url):
	#print(url)
	with open(url) as f:
		content = f.read()
	return bs4.BeautifulSoup(content, 'html.parser')


def iterate_files(dataframe):
	simple_soup, complex_soup = None, None
	text_complex, text_simple, text_complex_par, text_simple_par = "", "", "", ""
	for index, row in dataframe.iterrows():
		simple_soup, complex_soup = None, None
		saved = False
		if pd.isna(dataframe.loc[index, "simple_location_html"]):  # pd.isna(dataframe.loc[index, "complex_location_html"]) or
			continue
		elif dataframe.loc[index, "simple_location_html"].endswith(".html"):
			simple_soup = html2soup(dataframe.loc[index, "simple_location_html"])
		if not pd.isna(dataframe.loc[index, "complex_location_html"]) and dataframe.loc[index, "complex_location_html"].endswith(".html"):
			complex_soup = html2soup(dataframe.loc[index, "complex_location_html"])
		print(dataframe.loc[index, "simple_url"])
		if "offene-bibel" in dataframe.loc[index, "simple_url"]:
			text_simple, text_simple_par = extract_open_bible_text(simple_soup, "main", "class", "leichtesprache", "simple", dataframe.loc[index, "simple_url"], dataframe.loc[index, "last_access"])
			text_complex, text_complex_par = extract_open_bible_text(complex_soup, "div", "id", "Lesefassung", "complex", dataframe.loc[index, "complex_url"], dataframe.loc[index, "last_access"]) # Studienfassung
		# el
		# if "news-apa" in dataframe.loc[index, "website"]:
		# 	text_simple, text_complex = extract_news_apa_text(simple_soup, "div", "class", "apa-power-search-single__content", "simple",
		# 										  dataframe.loc[index, "simple_url"],
		# 										  dataframe.loc[index, "last_access"])
		elif "alumniportal-DE-2020" in dataframe.loc[index, "website"]:
			text_simple, text_simple_par = extract_alumni_portal(simple_soup, "h2", "", "A2", "simple",
												dataframe.loc[index, "simple_url"], dataframe.loc[index, "last_access"])
			text_complex, text_complex_par = extract_alumni_portal(simple_soup, "h2", "", "B2", "simple",
												 dataframe.loc[index, "simple_url"],
												 dataframe.loc[index, "last_access"])
		elif "alumniportal-DE-2021" in dataframe.loc[index, "website"]:
			text_simple, text_simple_par = extract_alumni_portal(simple_soup, "h2", "", "A2", "simple", dataframe.loc[index, "simple_url"],
												dataframe.loc[index, "last_access"])
			text_complex, text_complex_par = extract_alumni_portal(complex_soup, "h2", "", "B2", "complex", dataframe.loc[index, "complex_url"],
												 dataframe.loc[index, "last_access"])

		elif "apotheken-umschau" in dataframe.loc[index, "website"]:
			text_simple, text_simple_par = extract_apotheken_umschau(simple_soup, "article", "article-detail", "A2", "simple",
												dataframe.loc[index, "simple_url"],
												dataframe.loc[index, "last_access"])
			text_complex, text_complex_par = extract_apotheken_umschau(complex_soup, "article", "article-detail", "C2", "complex",
												 dataframe.loc[index, "complex_url"],
												 dataframe.loc[index, "last_access"])
		elif "news-apa-xml" in dataframe.loc[index, "website"]:
			parallel_docs = read_apa_xml("data/news-apa-xml/itrp-239068_topeasy.xml")
			i = 0
			for id, docs in parallel_docs.items():
				url = "https://science.apa.at/nachrichten-leicht-verstandlich/"
				text_simple, text_complex, text_simple_par, text_complex_par = extract_apa(docs, id, "HEAD", "", "", url, "2021-04-20")
				if text_simple != "# &copy; Origin: https://science.apa.at/nachrichten-leicht-verstandlich/ [last accessed: 2021-04-20]	\n":
					dataframe = save_data(dataframe, index, text_complex, text_simple, "data/news-apa-xml/txt/complex_"+str(i)+".txt", "data/news-apa-xml/txt/simple_"+str(i)+".txt")
					saved = True
					i += 1

		elif "bzfe" in dataframe.loc[index, "website"]:
			text_simple, text_simple_par = extract_bzfe(simple_soup, "div", "id", "content_article", "simple",
												dataframe.loc[index, "simple_url"],
												dataframe.loc[index, "last_access"])
			text_complex, text_complex_par = extract_bzfe(complex_soup, "div", "itemprop", "articleBody", "complex",
												 dataframe.loc[index, "complex_url"],
												 dataframe.loc[index, "last_access"])
		elif "einfach_politik" in dataframe.loc[index, "website"] or "junge_politik" in dataframe.loc[index, "website"]:
			text_simple, text_simple_par = extract_bpb(simple_soup, "section", "", "", "simple",
												dataframe.loc[index, "simple_url"],
												dataframe.loc[index, "last_access"])
			text_complex, text_complex_par = extract_bpb(complex_soup, "section", "", "", "complex",
												 dataframe.loc[index, "complex_url"],
												 dataframe.loc[index, "last_access"])
		elif "einfach-teilhaben" in dataframe.loc[index, "website"]:
			text_simple, text_simple_par = extract_einfach_teilhaben(simple_soup, "div", "class", "row detailseite", "simple",
												dataframe.loc[index, "simple_url"],
												dataframe.loc[index, "last_access"])
			text_complex, text_complex_par = extract_einfach_teilhaben(complex_soup, "div", "class", "row detailseite", "complex",
												 dataframe.loc[index, "complex_url"],
												 dataframe.loc[index, "last_access"])
		elif "stadt_hamburg" in dataframe.loc[index, "website"]:
			text_simple, text_simple_par = extract_hamburg(simple_soup, "div", "itemprop", "articleBody", "simple",
												dataframe.loc[index, "simple_url"],
												dataframe.loc[index, "last_access"])
			if not pd.isna(dataframe.loc[index, "complex_url"]) and "polizei.hamburg" in dataframe.loc[index, "complex_url"]:
				text_complex, text_complex_par = extract_hamburg(complex_soup, "span", "id", "articleText", "complex",
												 dataframe.loc[index, "complex_url"],
												 dataframe.loc[index, "last_access"])
			else:
				text_complex, text_complex_par = extract_hamburg(complex_soup, "div", "itemprop", "articleBody", "complex",
												 dataframe.loc[index, "complex_url"],
												 dataframe.loc[index, "last_access"])
		elif "stadt_koeln" in dataframe.loc[index, "website"]:
			text_simple, text_simple_par = extract_koeln(simple_soup, "main", "id", "inhalt", "simple",
												dataframe.loc[index, "simple_url"],
												dataframe.loc[index, "last_access"])
			text_complex, text_complex_par = extract_koeln(complex_soup, "main", "id", "inhalt", "complex",
												dataframe.loc[index, "complex_url"],
												dataframe.loc[index, "last_access"])
		elif "lebenshilfe_main_taunus" in dataframe.loc[index, "website"]:
			text_simple, text_simple_par = extract_lebenshilfe_main_taunus(simple_soup, "div", "class", "inhalt", "simple",
												dataframe.loc[index, "simple_url"],
												dataframe.loc[index, "last_access"])
			text_complex, text_complex_par = extract_lebenshilfe_main_taunus(complex_soup, "div", "class", "inhalt", "complex",
												dataframe.loc[index, "complex_url"],
												dataframe.loc[index, "last_access"])
		elif "easy_to_read_books" in dataframe.loc[index, "website"] or "passanten_verlag" in dataframe.loc[index, "website"] or "spaßamlesen_verlag" in dataframe.loc[index, "website"]:
			if not pd.isna(dataframe.loc[index, "simple_location_html"]):
				if dataframe.loc[index, "simple_location_html"].endswith(".pdf"):
					text_simple = extract_pdf(dataframe.loc[index, "simple_location_html"], "simple",
													dataframe.loc[index, "simple_url"],
													dataframe.loc[index, "last_access"],
													dataframe.loc[index, "simple_author"],
													dataframe.loc[index, "simple_title"])
				# elif dataframe.loc[index, "simple_location_html"].endswith(".html"):
				# 	text_simple = extract_html_book(dataframe.loc[index, "simple_location_html"], "simple",
				# 									dataframe.loc[index, "simple_url"],
				# 									dataframe.loc[index, "last_access"])
			if not pd.isna(dataframe.loc[index, "complex_location_html"]):
				if dataframe.loc[index, "complex_location_html"].endswith(".pdf"):
					text_complex = extract_pdf(dataframe.loc[index, "complex_location_html"], "complex",
													dataframe.loc[index, "complex_url"],
													dataframe.loc[index, "last_access"],
													dataframe.loc[index, "complex_author"],
													dataframe.loc[index, "complex_title"])
				elif dataframe.loc[index, "complex_location_html"].endswith(".html"):
					if "gutenberg" in dataframe.loc[index, "complex_url"]:
						text_complex, text_complex_par = extract_gutenberg(complex_soup, "body", "", "", "complex",
													dataframe.loc[index, "complex_url"],
													dataframe.loc[index, "last_access"])
			# print(text_simple, text_complex)
		elif "fairytales" == dataframe.loc[index, "website"]:
			if not pd.isna(dataframe.loc[index, "simple_location_html"]):
				if dataframe.loc[index, "simple_location_html"].endswith(".html"):
					text_simple, text_simple_par = extract_ndr_fairytales(simple_soup,
													dataframe.loc[index, "simple_url"],
													dataframe.loc[index, "last_access"])
			if not pd.isna(dataframe.loc[index, "complex_location_html"]):
				if dataframe.loc[index, "complex_location_html"].endswith(".html"):
					if "gutenberg" in dataframe.loc[index, "complex_url"]:
						text_complex, text_complex_par = extract_gutenberg(complex_soup, "body", "", "", "complex",
													dataframe.loc[index, "complex_url"],
													dataframe.loc[index, "last_access"])
		else:
			text_complex, text_simple = "", ""
			continue

		if not saved:
			dataframe = save_data(dataframe, index, text_complex, text_simple, text_complex_par, text_simple_par)

	return dataframe


def save_data(dataframe, index, text_complex, text_simple, text_complex_par, text_simple_par, text_path_complex=None, text_path_simple=None, text_path_simple_par=None, text_path_complex_par=None):
	if not text_path_simple and not pd.isna(dataframe.loc[index, "simple_location_html"]) and dataframe.loc[index, "simple_location_html"].endswith("html"):
		text_path_simple = dataframe.loc[index, "simple_location_html"].replace("html", "txt")
		text_path_simple_par = dataframe.loc[index, "simple_location_html"].replace("html", "txt_par")
	elif not text_path_simple and not pd.isna(dataframe.loc[index, "simple_location_html"]) and dataframe.loc[index, "simple_location_html"].endswith("pdf"):
		text_path_simple = dataframe.loc[index, "simple_location_html"].replace("pdf", "txt")
	if not text_path_complex and not pd.isna(dataframe.loc[index, "complex_location_html"]) and dataframe.loc[index, "complex_location_html"].endswith(".html"):
		text_path_complex = dataframe.loc[index, "complex_location_html"].replace("html", "txt")
		text_path_complex_par = dataframe.loc[index, "complex_location_html"].replace("html", "txt_par")
	elif not text_path_complex and not pd.isna(dataframe.loc[index, "complex_location_html"]) and dataframe.loc[index, "complex_location_html"].endswith(".pdf"):
		text_path_complex = dataframe.loc[index, "complex_location_html"].replace("pdf", "txt")
	if text_path_simple_par and not os.path.exists("/".join(text_path_simple_par.split("/")[:-1])):
		os.makedirs("/".join(text_path_simple_par.split("/")[:-1]))
	if text_path_simple and not os.path.exists("/".join(text_path_simple.split("/")[:-1])):
		os.makedirs("/".join(text_path_simple.split("/")[:-1]))
	if text_path_complex_par and not os.path.exists("/".join(text_path_complex_par.split("/")[:-1])):
		os.makedirs("/".join(text_path_complex_par.split("/")[:-1]))
	if text_path_complex and not os.path.exists("/".join(text_path_complex.split("/")[:-1])):
		os.makedirs("/".join(text_path_complex.split("/")[:-1]))
	if text_simple and text_path_simple:
		dataframe.loc[index, "simple_location_txt"] = text_path_simple
		with open(text_path_simple, "w", encoding="utf-8") as f:
			f.write(text_simple)
		if text_path_simple_par:
			dataframe.loc[index, "simple_location_txt_par"] = text_path_simple_par
			with open(text_path_simple_par, "w", encoding="utf-8") as f:
				f.write(text_simple_par)
	if text_complex and text_path_complex:
		dataframe.loc[index, "complex_location_txt"] = text_path_complex
		with open(text_path_complex, "w", encoding="utf-8") as f:
			f.write(text_complex)
		if text_path_complex_par:
			dataframe.loc[index, "complex_location_txt_par"] = text_path_complex_par
			with open(text_path_complex_par, "w", encoding="utf-8") as f:
				f.write(text_complex_par)
	return dataframe


def clean_data(text):
	for sign in [".", ",", "!", "?", ";", ":"]:
		text = text.replace(" "+sign, sign)
		text = text.replace(sign, sign+' ')
		text = text.replace("\n", " ")
		text = text.replace("  ", " ")
		text = text.replace("\t", " ")
	text = text.replace("\n", " ")
	text = text.replace("  ", " ")
	return text


def extract_open_bible_text(soup, tag, attribute, search_text, level, url, date):
	if not soup:
		return None, None
	title_item = soup.find("h1", {"id": "firstHeading"})
	if title_item:
		title = title_item.text.strip()
	else:
		title = "Unknown."
	container = soup.find(tag, {attribute: search_text})
	text = ""
	text_par = ""
	if container:
		for sup in container.find_all("sup"):
			sup.extract()
		for br in container.find_all("br"):
			br.extract()
		if level == "complex":
			# remove unwanted content
			for navi in container.find_all("p", {"class": "navi"}):
				navi.extract()
			for bracket in container.find_all("span", {"class": re.compile("runde-klammer.*")}):
				bracket.extract()
			for bracket in container.find_all("span", {"class": "eckige-klammer"}):
				bracket.extract()
		paragraphs = container.find_all(["p", "dl"])
		number_paragraphs = len(paragraphs)
		for i, par in enumerate(paragraphs):
			if level == "simple" and i+1 == number_paragraphs:
				pass
			else:
				text += par.text.strip()
				text_par += par.text.strip() + "SEPL|||SEPR"
				# if not par.text.endswith("\n"):
				# 	text += "\n"
	text = clean_data(text)
	text_par = clean_data(text_par)
	if not text and search_text != "Studienfassung":
		text, text_par = extract_open_bible_text(soup, tag, attribute, "Studienfassung", level, url, date)
	elif not text and not text_par:
		text = text
		text_par = text_par
	else:
		text = '# &copy; Origin: ' + str(url) + " [last accessed: " + str(date) + "]\t" + str(title) + "\n" + str(text)
		text_par = '# &copy; Origin: ' + str(url) + " [last accessed: " + str(date) + "]\t" + str(title) + "\n" + str(text_par)
	return text, text_par


def extract_news_apa_text(soup, tag, attribute, search_text, level, url, date):
	if not soup:
		return None, None
	title_item = soup.find("h3", {"class": "apa-power-search-single__title"})
	if title_item:
		title = title_item.text.strip()
	else:
		title = "Unknown."
	container = soup.find(tag, {attribute: search_text})
	simple_text = ""
	complex_text = ""
	current_text = complex_text
	if container:
		for i, par in enumerate(container.find_all("p")):
			if par.find("span"):
				span = par.find("span")
				if span.text == "Sprachstufe A2:":
					complex_text = current_text
					current_text = simple_text
				elif span.text == "Sprachstufe B1:":
					pass
				else:
					current_text += " " + span.text + ". "
			else:
				current_text += par.text + " "
	current_text = current_text.replace("\n", " ")
	current_text = current_text.replace("  ", " ")
	complex_text = complex_text.replace("\n", " ")
	complex_text = complex_text.replace("  ", " ")
	simple_text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + current_text.strip()
	complex_text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + complex_text.strip()
	return simple_text, complex_text


def add_apa_text(feld, text, text_par):
	for p in feld:
		if p.text:
			output = p.text.strip()
			output = output.replace("\n", " ")
			output = output.replace("  ", " ")
			if output.startswith("+++") and output.endswith("+++"):
				break
			if not output.endswith("."):
				text += output + ". "
				text_par += output + ". " + "SEPL|||SEPR"
			else:
				text += output + " "
				text_par += output + " " + "SEPL|||SEPR"
	return text, text_par


def extract_pdf(save_path, level, url, date, author=None, title=None, toc=True):
	text = ""
	end = False
	prev_line = ""
	try:
		with fitz.open(save_path) as doc:
			for page in doc:
				page_text = page.get_text("text")
				lines = page_text.split("\n")
				for n, line in enumerate(lines):
					text_line = "".join(line)
					# print("!!!"+text_line+"!!!")
					if text_line.endswith("-"):
						text_line = text_line[:-1]
					if re.match("^\D+ \| \d+", text_line) or (re.match("[\w\s\d]+", text_line) and re.match("\d+", prev_line) and re.match("\d+", "".join(lines[n+1]))):
						if not toc:
							text = ""
						toc = False
					elif re.match("^ISBN [\d-]+", text_line) or re.match("^ISBN E-Book [\d-]+", text_line) or re.match("^E-Book [\d-]+", text_line):
						toc = False
					elif re.match("\d+\. kapitel", text_line.lower()) or re.match("kapitel [VIX]+\s*", text_line.lower()):
						pass
					elif re.match("^\d+\s*$", text_line):
						# page number
						pass
					elif re.match("^�\d+", text_line) or re.match("^�\s?", text_line) or re.match("\s+", text_line):
						pass
					elif re.match("PASSANTENVERLAG", text_line.replace(" ", "")):
						pass
					elif not re.match("[A-z0-9]+", text_line):
						pass
					elif re.match("Bücher aus dem Passanten Verlag", text_line) or re.match("Ende der Leseprobe", text_line):
						end = True
						break
					elif not toc:
						text += text_line + " "
					prev_line = text_line
				if end:
					break
	except fitz.fitz.FileDataError:
		return ""
	if toc:
		text = extract_pdf(save_path, level, url, date, toc=False, author=author, title=title)

	for sign in [".", ",", "!", "?", ";", ":"]:
		text = text.replace(" "+sign, sign)
		text = text.replace(sign, sign+' ')
		text = text.replace("\t", " ")
		text = text.replace("\n", " ")
		text = text.replace("   ", " ")
		text = text.replace("  ", " ")
	if len(text) <= 500:
		return ""
	text = '# &copy; Origin: ' + str(url) + " [last accessed: " + str(date) + "]\t" + str(author) + "|" + str(title) + "\n" + str(text)
	return text.strip()


def extract_gutenberg(soup, tag, attribute, search_text, level, url, date):
	text, text_par = "", ""
	if not soup:
		return None, None
	title_item = soup.find("h5")
	if title_item:
		title = title_item.text.strip()
	else:
		title = ""
	content = soup.find(tag)
	for p in content.find_all("p"):
		text += clean_data(p.text.strip())
		text_par += clean_data(p.text.strip() + "SEPL|||SEPR ")
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text
	text_par = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text_par
	return text, text_par


def extract_ndr_fairytales(soup, url, date):
	text, text_par = "", ""
	content = soup.find("div", {"class": "modulepadding copytext"})
	title_item = content.find("header")
	if title_item:
		title = title_item.text.strip()
	else:
		title = "Unknown."
	for par in content.find_all("p"):
		for line in par:
			par_text = clean_data(line.text.strip())
			text += par_text
			text_par += par_text
		text_par += " SEPL|||SEPR"
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text
	text_par = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text_par
	return text, text_par


def extract_apa(soup, tag, attribute, search_text, level, url, date):
	if not soup:
		return None, None, None, None
	text_simple, text_complex = "", ""
	text_simple_par, text_complex_par = "", ""
	title_simple, title_complex = "", ""
	for doc in soup:
		complex, simple = False, False
		for feld in doc.find(attribute):
			if feld.attrib["NAME"] == "INHALT":
				if complex:
					text_complex, text_complex_par = add_apa_text(feld, text_complex, text_complex_par)
				elif simple:
					text_simple, text_simple_par = add_apa_text(feld, text_simple, text_simple_par)
			elif feld.attrib["NAME"] == "TITEL":
				if "Sprachstufe B1" in feld[0].text:
					title_complex = feld[0].text.strip() + " vom "+tag + " ("+ doc.get("NAME")+")"
					complex = True
				elif "Sprachstufe A2" in feld[0].text:
					title_simple = feld[0].text.strip() + " vom "+tag + " ("+ doc.get("NAME")+")"
					simple = True
	text_simple = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title_simple + "\n" + text_simple
	text_complex= '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title_complex + "\n" + text_complex
	text_simple_par = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title_simple + "\n" + text_simple_par
	text_complex_par = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title_complex + "\n" + text_complex_par

	return text_simple, text_complex, text_simple_par, text_complex_par


def read_apa_xml(filename):
	root = ET.parse(filename).getroot()
	all_recdates = dict()
	for doc in root:
		recdate_doc = doc.get("RECDATE")
		if recdate_doc in all_recdates.keys():
			all_recdates[recdate_doc].append(doc)
		else:
			all_recdates[recdate_doc] = [doc]
	parallel_docs = {key: value for key, value in all_recdates.items() if len(value) > 1}
	return parallel_docs


def extract_alumni_portal(soup, tag, attribute, search_text, level, url, date):
# def extract_alumni_portal(soup, url, tag, search_text):
	if not soup:
		return None, None
	text, text_par = "", ""
	search_text_level = "sprachniveau "+search_text.lower()
	title_item = soup.find("h1")
	if title_item:
		title = title_item.text.strip()
	else:
		title = "Unknown."
	headline = soup.find(tag, text=lambda x: x and search_text_level in x.lower())
	if headline:
		paragraphs = headline.parent.find_all("p", {"class": ""})
		if paragraphs:
			for i_par, par in enumerate(paragraphs):
				if par.text.strip().startswith("Fragen B2") or par.text.strip().startswith("Frage B2") or \
						par.text.strip().startswith("Fragen A2") or par.text.strip().startswith("Frage A2") or \
						par.text.strip().startswith("Haben Sie die Texte gelesen und verstanden?") or \
						par.text.strip().startswith("Text und Antworten in der Community") or par.text.strip().startswith("Haben Sie den Text gelesen und verstanden?"):
					break
				else:
					text += par.text.strip()
					text_par += par.text.strip()  + "SEPL|||SEPR"
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text
	text_par = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text_par
	return text, text_par


def extract_apotheken_umschau(soup, tag, attribute, search_text, level, url, date):
	if not soup:
		return None, None
	text, text_par = "", ""
	title_item = soup.find("h1")
	if title_item:
		title = title_item.text.strip()
	else:
		title = "Unknown."
	content = soup.find(tag)
	if content:
		paragraphs = content.find_all(["p", "li"])
		headlines = content.find_all("h2")
		if paragraphs:
			for par in paragraphs:
				if par.text.strip().startswith("Sie wollen noch mehr über "):
					break
				elif par.has_attr("class") and "text" in par["class"]:
					if par.text.strip().endswith(":"):
						text += par.text.strip() + " "
					else:
						text += par.text.strip() + " " + "SEPL|||SEPR"
				# elif par.has_attr("class") and par["class"] != "text":
				# 	pass
				# elif not par.has_attr("class"):
				# 	pass
				elif par.parent.name == "ul" and not par.has_attr("class") and par != par.parent.find_all("li")[-1]:
					text += par.text.strip() + ", "
					text_par += par.text.strip() + ", "
				elif par.parent.name == "ul" and not par.has_attr("class"):
					text += par.text.strip() + ". "
					text_par += par.text.strip() + ". " + "SEPL|||SEPR"
		if headlines:
			for headline in headlines:
				text += headline.text.strip() + " "
				text_par += headline.text.strip() + " "
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text
	text_par = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text_par
	return text, text_par


def extract_bzfe(soup, tag, attribute, search_text, level, url, date):
	if not soup:
		return None, None
	title_item = soup.find("span", {"itemprop": "headline"})
	if title_item:
		title = title_item.text.strip().split("\n")[0]
	else:
		title = "Unknown."
	container = soup.find(tag, {attribute: search_text})
	text, text_par = "", ""
	if container:
		for table in container.find_all("table"):
			table.extract()
		for i, par in enumerate(container.find_all(["p"])):
			text += par.text.strip()+" "
			text_par += par.text.strip() + " " + "SEPL|||SEPR"

	text = clean_data(text)
	text_par = clean_data(text_par)
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text.strip()
	text_par = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text_par.strip()
	return text, text_par


def extract_bpb(soup, tag, attribute, search_text, level, url, date):
	if not soup:
		return None, None
	title_item = soup.find("h1")
	if title_item:
		title = title_item.text.strip()
	else:
		title = "Unknown."
	container = soup.find(tag)
	text, text_par = "", ""
	source = ""
	if container:
		for unwanted in container.find_all(["h1", "h2", "h3", "br"]):
			unwanted.extract()
		for image in container.find_all("div", {"class": lambda value: value and value.startswith('article_image')}):
			image.extract()
		for list_item in container.find_all("li"):
			if list_item.text and not list_item.text.strip().endswith((",",".")):
				list_item.string = list_item.text.strip()+", "
		for item in container.find_all("b"):
			if item.text == "Siehe auch:":
				next_url = True
				while next_url == True:
					nextNode = item.find_next_sibling("a")
					if nextNode:
						nextNode.extract()
					else:
						next_url = False
			item.extract()
		for item in container.find_all("i"):
			if item.text.strip().startswith("Quelle: "):
				source = item.text.strip()[8:]
			item.extract()
		#for element in container.findAll(text=True):
		#	text += element.text.strip() + " "

		text += container.text.strip() +" "
	text_par = text.replace("\n\n", "SEPL|||SEPR")
	text = re.sub("\[.*\]", "", text)
	text = clean_data(text)
	text_par = re.sub("\[.*\]", "", text_par)
	text_par = clean_data(text_par)
	if source:
		text = '# &copy; Origin: ' + url +"("+source+")" + " [last accessed: " + date + "]\t" + title + "\n" + text.strip()
		text_par = '# &copy; Origin: ' + url +"("+source+")" + " [last accessed: " + date + "]\t" + title + "\n" + text_par.strip()
	else:
		text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text.strip()
		text_par = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text_par.strip()
	return text, text_par


def extract_einfach_teilhaben(soup, tag, attribute, search_text, level, url, date):
	if not soup:
		return None, None
	title_item = soup.find("h1", {"class": "seitenumschaltung__headline"})
	if title_item:
		title = title_item.text.strip()
	else:
		title = "Unknown."
	container = soup.find(tag, {attribute: search_text})
	text, text_par = "", ""
	if container:
		for list_item in container.find_all("li"):
			if list_item.text and not list_item.text.strip().endswith((".", ",", "!", "?", ";", ":")):
				list_item.string = list_item.text.strip()+", "
		for table in container.find_all("table"):
			table.extract()
		for item in container.find_all("div", {"class": "sectionRelated"}):
			item.extract()
		for item in container.find_all("div", {"class": "embedded_navigation fullContent"}):
			item.extract()
		for item in container.find_all("div", {"class": "togglemodul bereichsthemen gsb-toggle"}):
			item.extract()
		for i, par in enumerate(container.find_all(["p", "ul"])):
			text += par.text.strip()+" "
			text_par += par.text.strip()+" "+"SEPL|||SEPR"


	text = clean_data(text)
	text_par = clean_data(text_par)
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text.strip()
	text_par = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text_par.strip()
	return text, text_par


def extract_hamburg(soup, tag, attribute, search_text, level, url, date):
	if not soup:
		return None, None
	title = soup.find("span", {"id": "title"}).text.strip()
	container = soup.find(tag, {attribute: search_text})
	# print("hamburg", container)
	text, text_par = "", ""
	if container:
		for item in container.find_all("a"):
			if item.text.startswith("http"):
				item.extract()
		for list_item in container.find_all("li"):
			if list_item.text and not list_item.text.strip().endswith((".", ",", "!", "?", ";", ":")):
				list_item.string = list_item.text.strip()+", "
		for list_item in container.find_all("p"):
			if list_item.text and not list_item.text.strip().endswith((".", ",", "!", "?", ";", ":")):
				list_item.string = list_item.text.strip()+". "
		for table in container.find_all("table"):
			table.extract()
		for item in container.find_all("div", {"class": "masonry-helper"}):
			item.extract()
		for item in container.find_all("div", {"class": "teaser teaser-thumb teaser-thumb-article"}):
			item.extract()
		for i, par in enumerate(container.find_all(["p", "ul"])):
			text += par.text.strip()+" "
			text_par += par.text.strip()+" " + "SEPL|||SEPR"

	text = clean_data(text)
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text.strip()
	text_par = clean_data(text_par)
	text_par = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text_par.strip()
	return text, text_par


def extract_koeln(soup, tag, attribute, search_text, level, url, date):
	if not soup:
		return None, None
	title_item = soup.find("h1", {"class": "articlehead"})
	if title_item:
		title = title_item.text.strip()
	else:
		title = "Unknown."
	text, text_par = "", ""
	container = soup.find(tag, {attribute: search_text})
	if container:
		for item in container.find_all(["h2", "p", "li"]):
			if item.text.strip() in ["Ähnliche Themen in Alltags-Sprache", "Weitere Infos", "War dieser Artikel hilfreich für Sie?"]:
				break
			elif item.text.strip() and not item.text.strip()[-1] in [".", ",", "!", "?", ";", ":"]:
				text += item.text.strip()+". "
				text_par += item.text.strip()+". "  + "SEPL|||SEPR"
			else:
				text += item.text.strip()+" "
				text_par += item.text.strip()+" "  + "SEPL|||SEPR"
	text = clean_data(text)
	text_par = clean_data(text_par)
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text.strip()
	text_par = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text_par.strip()
	return text, text_par


def extract_lebenshilfe_main_taunus(soup, tag, attribute, search_text, level, url, date):
	if not soup:
		return None, None
	title_item = soup.find("h1")
	if title_item:
		title = title_item.text.strip()
	else:
		title = "Unknown."
	text, text_par = "", ""
	container = soup.find(tag, {attribute: search_text})
	if container:
		for item in container.find_all(["p", "ul"], recursive=False):
			text += item.text.strip()+" "
			text_par += item.text.strip() + " "  + "SEPL|||SEPR"
	text = clean_data(text)
	text_par = clean_data(text_par)
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text.strip()
	text_par = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text_par.strip()
	return text, text_par


def main():
	input_dir = "data/"
	input_file = input_dir+"url_overview.tsv"
	dataframe = pd.read_csv(input_file, sep="\t", header=0)
	# todo remove books from list
	# filter_data = ("website", "passanten_verlag")
	# filter_data = ("website", "lebenshilfe_main_taunus")  # bible_verified + # news-apa # "alumniportal-DE-2021" # "apotheken-umschau"
	output_dataframe = filter_and_extract_data(dataframe)  #  , filter_data)
	output_dataframe.to_csv(input_dir+"url_overview_text.tsv", header=True, index=False, sep="\t")


if __name__ == "__main__":
	main()
