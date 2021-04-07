import os, re, csv, requests
from pathlib import Path
import bs4
import urllib.request
from datetime import datetime
import pandas as pd
import stanza
from spacy_stanza import StanzaLanguage


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
		if pd.isna(dataframe.loc[index, "complex_location_html"]) or pd.isna(dataframe.loc[index, "simple_location_html"]):
			continue
		simple_soup = html2soup(dataframe.loc[index, "simple_location_html"])
		complex_soup = html2soup(dataframe.loc[index, "complex_location_html"])
		print(dataframe.loc[index, "simple_url"])
		# if "offene-bibel" in dataframe.loc[index, "simple_url"]:
		# 	text_simple = extract_open_bible_text(simple_soup, "main", "class", "leichtesprache", "simple", dataframe.loc[index, "simple_url"], dataframe.loc[index, "last_access"])
		# 	text_complex = extract_open_bible_text(complex_soup, "div", "id", "Studienfassung", "complex", dataframe.loc[index, "complex_url"], dataframe.loc[index, "last_access"])
		# el
		# if "news-apa" in dataframe.loc[index, "website"]:
		# 	text_simple, text_complex = extract_news_apa_text(simple_soup, "div", "class", "apa-power-search-single__content", "simple",
		# 										  dataframe.loc[index, "simple_url"],
		# 										  dataframe.loc[index, "last_access"])
		if "alumniportal-DE-2020" in dataframe.loc[index, "website"]:
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
		else:
			continue

		dataframe = save_data(dataframe, index, text_complex, text_simple)

	return dataframe


def save_data(dataframe, index, text_complex, text_simple):
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
	title = soup.find("h1", {"class": "firstHeading"})
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
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text
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
		paragraphs = content.find_all("p", {"class": "text"})
		headlines = content.find_all("h2")
		if paragraphs:
			for par in paragraphs:
				if par.text.strip().startswith("Sie wollen noch mehr über "):
					break
				else:
					text += par.text.strip() + " "
		if headlines:
			for headline in headlines:
				text += headline.text.strip() + " "
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\t" + title + "\n" + text
	return text

def main():
	input_dir = "data/"
	input_file = input_dir+"url_overview_2021-04-07-17:47.tsv"
	dataframe = pd.read_csv(input_file, sep="\t", header=0)
	filter_data = ("website", "apotheken-umschau")  # bible_verified + # news-apa # "alumniportal-DE-2021"
	output_dataframe = filter_and_extract_data(dataframe, filter_data)
	output_dataframe.to_csv(input_dir+"url_overview_alumni_txt.tsv", header=True, index=False, sep="\t")


if __name__ == "__main__":
	main()
