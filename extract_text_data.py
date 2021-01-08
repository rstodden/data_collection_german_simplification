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
		if "offene-bibel" in dataframe.loc[index, "simple_url"]:
			text_simple = extract_open_bible_text(simple_soup, "main", "class", "leichtesprache", "simple", dataframe.loc[index, "simple_url"], dataframe.loc[index, "last_access"])
			text_complex = extract_open_bible_text(complex_soup, "div", "id", "Studienfassung", "complex", dataframe.loc[index, "complex_url"], dataframe.loc[index, "last_access"])

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
	container = soup.find(tag, {attribute: search_text})
	text = ""
	if container:
		for sup in container.find_all("sup"):
			sup.extract()
		for br in container.find_all("br"):
			br.extract()
		if level == "complex":
			for navi in container.find_all("p", {"class": "navi"}):
				navi.extract()
			for bracket in container.find_all("span", {"class": re.compile(".*klammer.*")}):
				bracket.extract()
		paragraphs = container.find_all("p")
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
	text = '# &copy; Origin: ' + url + " [last accessed: " + date + "]\n" + text
	return text


def main():
	input_dir = "data/"
	input_file = input_dir+"url_overview.tsv"
	dataframe = pd.read_csv(input_file, sep="\t", header=0)
	filter_data = None # ("website", "bible_verified")
	output_dataframe = filter_and_extract_data(dataframe, filter_data)
	output_dataframe.to_csv(input_dir+"url_overview_txt.tsv", header=True, index=False, sep="\t")

if __name__ == "__main__":
	main()