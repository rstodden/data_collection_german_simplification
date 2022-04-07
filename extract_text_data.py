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
	output_simple, output_complex = "", ""
	for index, row in dataframe.iterrows():
		saved = False
		if pd.isna(dataframe.loc[index, "complex_location_html"]) or pd.isna(dataframe.loc[index, "simple_location_html"]):
			continue
		simple_soup = html2soup(dataframe.loc[index, "simple_location_html"])
		complex_soup = html2soup(dataframe.loc[index, "complex_location_html"])
		print(dataframe.loc[index, "simple_url"])
		if "offene-bibel" in dataframe.loc[index, "simple_url"]:
		 	text_simple = extract_open_bible_text(simple_soup, "main", "class", "leichtesprache", "simple", dataframe.loc[index, "simple_url"], dataframe.loc[index, "last_access"])
		 	text_complex = extract_open_bible_text(complex_soup, "div", "id", "Lesefassung", "complex", dataframe.loc[index, "complex_url"], dataframe.loc[index, "last_access"]) # Studienfassung
		# el
		# if "news-apa" in dataframe.loc[index, "website"]:
		# 	text_simple, text_complex = extract_news_apa_text(simple_soup, "div", "class", "apa-power-search-single__content", "simple",
		# 										  dataframe.loc[index, "simple_url"],
		# 										  dataframe.loc[index, "last_access"])
		elif "alumniportal-DE-2020" in dataframe.loc[index, "website"]:
			text_simple = extract_alumni_portal(simple_soup, "h2", "", "A2", "simple",
												dataframe.loc[index, "simple_url"], dataframe.loc[index, "last_access"])
			text_complex = extract_alumni_portal(simple_soup, "h2", "", "B2", "simple",
												 dataframe.loc[index, "simple_url"],
												 dataframe.loc[index, "last_access"])
		elif "alumniportal-DE-2021" in dataframe.loc[index, "website"]:
			text_simple = extract_alumni_portal(simple_soup, "h2", "", "A2", "simple", dataframe.loc[index, "simple_url"],
												dataframe.loc[index, "last_access"])
			text_complex = extract_alumni_portal(complex_soup, "h2", "", "B2", "complex", dataframe.loc[index, "complex_url"],
												 dataframe.loc[index, "last_access"])

		elif "apotheken-umschau" in dataframe.loc[index, "website"]:
			text_simple = extract_apotheken_umschau(simple_soup, "article", "article-detail", "A2", "simple",
												dataframe.loc[index, "simple_url"],
												dataframe.loc[index, "last_access"])
			text_complex = extract_apotheken_umschau(complex_soup, "article", "article-detail", "C2", "complex",
												 dataframe.loc[index, "complex_url"],
												 dataframe.loc[index, "last_access"])
		elif "news-apa-xml" in dataframe.loc[index, "website"]:
			parallel_docs = read_apa_xml("data/news-apa-xml/itrp-239068_topeasy.xml")
			i = 0
			for id, docs in parallel_docs.items():
				url = "https://science.apa.at/nachrichten-leicht-verstandlich/"
				text_simple, text_complex = extract_apa(docs, id, "HEAD", "", "", url, "2021-04-20")
				if text_simple != "# &copy; Origin: https://science.apa.at/nachrichten-leicht-verstandlich/ [last accessed: 2021-04-20]	\n":
					dataframe = save_data(dataframe, index, text_complex, text_simple, "data/news-apa-xml/txt/complex_"+str(i)+".txt", "data/news-apa-xml/txt/simple_"+str(i)+".txt")
					saved = True
					i += 1

		elif "bzfe" in dataframe.loc[index, "website"]:
			text_simple = extract_bzfe(simple_soup, "div", "id", "content_article", "simple",
												dataframe.loc[index, "simple_url"],
												dataframe.loc[index, "last_access"])
			text_complex = extract_bzfe(complex_soup, "div", "itemprop", "articleBody", "complex",
												 dataframe.loc[index, "complex_url"],
												 dataframe.loc[index, "last_access"])
		elif "einfach_politik" in dataframe.loc[index, "website"] or "junge_politik" in dataframe.loc[index, "website"]:
			text_simple = extract_bpb(simple_soup, "section", "", "", "simple",
												dataframe.loc[index, "simple_url"],
												dataframe.loc[index, "last_access"])
			text_complex = extract_bpb(complex_soup, "section", "", "", "complex",
												 dataframe.loc[index, "complex_url"],
												 dataframe.loc[index, "last_access"])
		elif "einfach-teilhaben" in dataframe.loc[index, "website"]:
			text_simple = extract_einfach_teilhaben(simple_soup, "div", "class", "row detailseite", "simple",
												dataframe.loc[index, "simple_url"],
												dataframe.loc[index, "last_access"])
			text_complex = extract_einfach_teilhaben(complex_soup, "div", "class", "row detailseite", "complex",
												 dataframe.loc[index, "complex_url"],
												 dataframe.loc[index, "last_access"])
		elif "stadt_hamburg" in dataframe.loc[index, "website"]:
			text_simple = extract_hamburg(simple_soup, "div", "itemprop", "articleBody", "simple",
												dataframe.loc[index, "simple_url"],
												dataframe.loc[index, "last_access"])
			if "polizei.hamburg" in dataframe.loc[index, "complex_url"]:
				text_complex = extract_hamburg(complex_soup, "span", "id", "articleText", "complex",
												 dataframe.loc[index, "complex_url"],
												 dataframe.loc[index, "last_access"])
			else:
				text_complex = extract_hamburg(complex_soup, "div", "itemprop", "articleBody", "complex",
												 dataframe.loc[index, "complex_url"],
												 dataframe.loc[index, "last_access"])
		else:
			text_complex, text_simple = "", ""
			continue

		if not saved:
			dataframe = save_data(dataframe, index, text_complex, text_simple)

	return dataframe


def save_data(dataframe, index, text_complex, text_simple, text_path_complex=None, text_path_simple=None):
	if not text_path_complex and not text_path_simple:
		text_path_complex = dataframe.loc[index, "complex_location_html"].replace("html", "txt")
		text_path_simple = dataframe.loc[index, "simple_location_html"].replace("html", "txt")
	if not os.path.exists("/".join(text_path_simple.split("/")[:-1])):
		os.makedirs("/".join(text_path_simple.split("/")[:-1]))
	dataframe.loc[index, "simple_location_txt"] = text_path_simple
	dataframe.loc[index, "complex_location_txt"] = text_path_complex
	with open(text_path_complex, "w", encoding="utf-8") as f:
		f.write(text_complex)
	with open(text_path_simple, "w", encoding="utf-8") as f:
		f.write(text_simple)
	return dataframe


def extract_open_bible_text(soup, tag, attribute, search_text, level, url, date):
	title = soup.find("h1", {"id": "firstHeading"}).text
	container = soup.find(tag, {attribute: search_text})
	text = ""
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
				# if not par.text.endswith("\n"):
				# 	text += "\n"
	for sign in [".", ",", "!", "?", ";", ":"]:
		text = text.replace(" "+sign, sign)
		text = text.replace(sign, sign+' ')
		text = text.replace("\n", " ")
		text = text.replace("  ", " ")
		text = text.replace("\t", " ")
	if not text and search_text != "Studienfassung":
		text = extract_open_bible_text(soup, tag, attribute, "Studienfassung", level, url, date)
	elif not text:
		text = text
	else:
		text = '# &copy; Origin: ' + str(url) + " [last accessed: " + str(date) + "]\t" + str(title) + "\n" + str(text)
	return text


def extract_news_apa_text(soup, tag, attribute, search_text, level, url, date):
	title = soup.find("h3", {"class": "apa-power-search-single__title"}).text.strip()
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


def add_apa_text(feld, text):
	for p in feld:
		if p.text:
			output = p.text.strip()
			output = output.replace("\n", " ")
			output = output.replace("  ", " ")
			if output.startswith("+++") and output.endswith("+++"):
				break
			if not output.endswith("."):
				text += output + ". "
			else:
				text += output + " "
	return text


def extract_apa(soup, tag, attribute, search_text, level, url, date):
	text_simple, text_complex = "", ""
	title_simple, title_complex = "", ""
	for doc in soup:
		complex, simple = False, False
		for feld in doc.find(attribute):
			if feld.attrib["NAME"] == "INHALT":
				if complex:
					text_complex = add_apa_text(feld, text_complex)
				elif simple:
					text_simple = add_apa_text(feld, text_simple)
			elif feld.attrib["NAME"] == "TITEL":
				if "Sprachstufe B1" in feld[0].text:
					title_complex = feld[0].text.strip() + " vom "+tag + " ("+ doc.get("NAME")+")"
					complex = True
				elif "Sprachstufe A2" in feld[0].text:
					title_simple = feld[0].text.strip() + " vom "+tag + " ("+ doc.get("NAME")+")"
					simple = True
	text_simple = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title_simple + "\n" + text_simple
	text_complex= '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title_complex + "\n" + text_complex

	return text_simple, text_complex


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
	text = ""
	search_text_level = "sprachniveau "+search_text.lower()
	title = soup.find("h1").text
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
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text
	return text


def extract_apotheken_umschau(soup, tag, attribute, search_text, level, url, date):
	text = ""
	title = soup.find("h1").text
	content = soup.find(tag)
	if content:
		paragraphs = content.find_all(["p", "li"])
		headlines = content.find_all("h2")
		if paragraphs:
			for par in paragraphs:
				if par.text.strip().startswith("Sie wollen noch mehr über "):
					break
				elif par.has_attr("class") and "text" in par["class"]:
					text += par.text.strip() + " "
				# elif par.has_attr("class") and par["class"] != "text":
				# 	pass
				# elif not par.has_attr("class"):
				# 	pass
				elif par.parent.name == "ul" and not par.has_attr("class") and par != par.parent.find_all("li")[-1]:
					text += par.text.strip() + ", "
				elif par.parent.name == "ul" and not par.has_attr("class"):
					text += par.text.strip() + ". "
		if headlines:
			for headline in headlines:
				text += headline.text.strip() + " "
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text
	return text

def extract_bzfe(soup, tag, attribute, search_text, level, url, date):
	title = soup.find("span", {"itemprop": "headline"}).text.strip().split("\n")[0]
	container = soup.find(tag, {attribute: search_text})
	text = ""
	if container:
		for table in container.find_all("table"):
			table.extract()
		for i, par in enumerate(container.find_all(["p"])):
			text += par.text.strip()+" "
			
			
	for sign in [".", ",", "!", "?", ";", ":"]:
		text = text.replace(" "+sign, sign)
		text = text.replace(sign, sign+' ')
		text = text.replace("\t", " ")
	text = text.replace("\n", " ")
	text = text.replace("  ", " ")
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text.strip()
	return text
	
def extract_bpb(soup, tag, attribute, search_text, level, url, date):
	title = soup.find("h1").text.strip()
	container = soup.find(tag)
	text = ""
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
			
			
	"""for sign in [".", ",", "!", "?", ";", ":"]:
		text = text.replace(" "+sign, sign)
		text = text.replace(sign, sign+' ')
		text = text.replace("\t", " ")"""
	text = re.sub("\[.*\]", "", text)
	text = text.replace("\n", " ")
	text = text.replace("  ", " ")
	if source:
		text = '# &copy; Origin: ' + url +"("+source+")" + " [last accessed: " + date + "]\t" + title + "\n" + text.strip()
	else:
		text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text.strip()
	return text
	
def extract_einfach_teilhaben(soup, tag, attribute, search_text, level, url, date):
	title = soup.find("h1", {"class": "seitenumschaltung__headline"}).text.strip()
	container = soup.find(tag, {attribute: search_text})
	text = ""
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
			
			
	for sign in [".", ",", "!", "?", ";", ":"]:
		text = text.replace(" "+sign, sign)
		text = text.replace(sign, sign+' ')
		text = text.replace("\t", " ")
	text = text.replace("\n", " ")
	text = text.replace("  ", " ")
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text.strip()
	return text

def extract_hamburg(soup, tag, attribute, search_text, level, url, date):
	title = soup.find("span", {"id": "title"}).text.strip()
	container = soup.find(tag, {attribute: search_text})
	# print("hamburg", container)
	text = ""
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
			
	for sign in [".", ",", "!", "?", ";", ":"]:
		text = text.replace(" "+sign, sign)
		text = text.replace(sign, sign+' ')
		text = text.replace("\t", " ")
	text = text.replace("\n", " ")
	text = text.replace("  ", " ")
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text.strip()
	return text


def main():
	input_dir = "data/"
	input_file = input_dir+"url_overview.tsv"
	dataframe = pd.read_csv(input_file, sep="\t", header=0)
	filter_data = ("website", "stadt_hamburg")  # bible_verified + # news-apa # "alumniportal-DE-2021" # "apotheken-umschau"
	output_dataframe = filter_and_extract_data(dataframe, filter_data)
	output_dataframe.to_csv(input_dir+"url_overview_text_problematic.tsv", header=True, index=False, sep="\t")


if __name__ == "__main__":
	main()
