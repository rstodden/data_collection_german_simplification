import os, re, csv, requests
from pathlib import Path
import bs4
import urllib.request
from datetime import datetime
import pandas as pd
import stanza
from spacy_stanza import StanzaLanguage


# docs, n_sents, n_token = 0, 0, 0

def do_stuff(dataframe, filter=None):
	if filter:
		column, value = filter
		dataframe = dataframe.loc[dataframe[column] == value]
	simple_locations = dataframe["simple_location"]
	complex_locations = dataframe["complex_location"]
	output_simple = iterate_files(simple_locations, "simple")
	output_complex = iterate_files(complex_locations, "complex")

	with open("output_test_simple.txt", "w") as f:
		f.write(output_simple)
	with open("output_test_complex.txt", "w") as f:
		f.write(output_complex)


def html2soup(url):
	with open(url) as f:
		content = f.read()
	return bs4.BeautifulSoup(content, 'html.parser')


def iterate_files(location, level):
	output = "# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC\n"
	counter_dict = dict()
	for url in location:
		# n_docs += 1

		print(url)
		soup = html2soup(url)
		identifier = url.split(".html")[0]
		"""name = identifier.split("/")[1]
		if name in counter_dict.keys():
			counter_dict[name] += 1
		else:
			counter_dict[name] = 1
		if counter_dict[name] >= 2:
			continue"""
		output += "# newdoc id = "+identifier+"\n"
		if "alumniportal-DE" in url:
			if level == "simple":
				output += extract_alumni_portal(soup, identifier, "h2", "Sprachniveau A2")
			elif level == "complex":
				output += extract_alumni_portal(soup, identifier, "h2", "Sprachniveau B2")
			else:
				print("Something went wrong here.")
		elif "lebenshilfe_main_taunus" in url:
			if level == "simple":
				output += extract_lebenshilfe(soup, identifier, "div", "class", "inhalt")
			elif level == "complex":
				output += extract_lebenshilfe(soup, identifier, "div", "class", "inhalt")
			else:
				print("Something went wrong here.")
		elif "os-hho" in url:
			pass
			"""if level == "simple":
				output += extract_os_hho(soup, identifier, "h1")
			elif level == "complex":
				output += extract_os_hho(soup, identifier, "div", "class", "inhalt")
			else:
				print("Something went wrong here.")"""
		elif "einfach-teilhaben" in url:
			if level == "simple":
				output += extract_einfach_teilhaben(soup, identifier, "div", "class", "detailseite")
			elif level == "complex":
				output += extract_einfach_teilhaben(soup, identifier, "div", "class", ["detailseite__right", "detailseite"])
			else:
				print("Something went wrong here.")
		elif "bible" in url:
			if level == "simple":
				output += extract_bible(soup, identifier, "div", "id", "LeichteSprache")
			#elif level == "complex":
			#	output += extract_bible(soup, identifier, "div", "id", "Studienfassung")
			else:
				print("Something went wrong here.")

		else:
			return ""
	return output


def extract_alumni_portal(soup, url, tag, search_text):
	output = ""
	headline = soup.find(tag, text=lambda x: x and search_text in x)
	if headline:
		paragraphs = headline.parent.find_all("p", {"class": ""})
		if paragraphs:
			for i_par, par in enumerate(paragraphs):
				output += "# newpar id = "+ url+"_"+str(i_par)+"\n"
				output += text2conll(par.text, url, i_par)
	return output


def extract_lebenshilfe(soup, url, tag, attribute, search_text):
	output = ""
	container = soup.find(tag, {attribute: search_text})
	if container:
		paragraphs = container.find_all("p")
		if paragraphs:
			for i_par, par in enumerate(paragraphs):
				if par.text and not re.search(r"^\s", par.text):
					output += "# newpar id = "+ url+"_"+str(i_par)+"\n"
					output += text2conll(par.text, url, i_par)
	return output


def extract_os_hho(soup, url, tag):
	output = ""
	container = soup.find(tag)
	print(container)
	print(container.next_sibling.string)
	if container:
		text, i_par = "", 0
		for element in container:
			if isinstance(element, bs4.NavigableString):
				return ""
			elif element.name == 'br' and element.next_sibling and element.next_sibling.name == "br":
				output += "# newpar id = " + url + "_" + str(i_par) + "\n"
				print(text)
				output += text2conll(text, url, i_par)
				i_par += 1
			else:
				text += element.text
	return output


def extract_einfach_teilhaben(soup, url, tag, attribute, search_text):
	output, container = "", ""
	if isinstance(search_text, list):
		for text in search_text:
			if soup.find(tag, {attribute: text}):
				container = soup.find(tag, {attribute: text})
				break
	else:
		container = soup.find(tag, {attribute: search_text})
	if container:
		paragraphs = container.find_all("p")
		if paragraphs:
			for i_par, par in enumerate(paragraphs):
				if par.text and not re.search(r"^\s", par.text):
					output += "# newpar id = "+ url+"_"+str(i_par)+"\n"
					output += text2conll(par.text, url, i_par)
	return output


def extract_bible(soup, url, tag, attribute, search_text):
	output = ""
	container = soup.find(tag, {attribute: search_text})
	if container:
		paragraphs = container.find_all("p", recursive=False)
		if paragraphs:
			for i_par, par in enumerate(paragraphs):
				if par.text and not re.search(r"^\s", par.text):
					output += "# newpar id = "+ url+"_"+str(i_par)+"\n"
					output += text2conll(par.text, url, i_par)
	return output


def text2conll(sent_string, url, i_par):
	output = ""
	# parse the sentence string with Spacy using the language model for German
	doc = nlp(sent_string)

	# loop through the elements of the spacy parse
	for i_sent, s in enumerate(doc.sents):
		# n_sents += 1
		output += "# sent_id = "+url+"_"+str(i_par)+"_"+str(i_sent)+"\n# text = "+s.text+"\n"

		# we use enumerate to count the tokens in sentences
		for i, w in enumerate(s):
			# n_token += 1
			# in spacy, you can find the head of each token using .head
			# + 1 is needed to increase the index of each word by i
			head_idx = doc[i].head.i + 1

			# for each token, we create a line with information from the spacy parse.
			line = "%d\t%s\t%s\t%s\t%s\t%s\t%d\t%s\t%s\t%s\n" % (i + 1, w, w.lemma_, w.pos_,  w.tag_, "_", head_idx, w.dep_, "_", "_")

			# we need to change the head of the token to "0", if this token is the root of the sentence
			if 'ROOT' in line:
				line = re.sub('[0-9]+\tROOT', '0\tROOT', line)  # replace root head with 0

			# append the line to the string
			output += line
		output += "\n"
	# return the whole spacy parse as a string
	return output


def main():
	global nlp
	#global n_docs
	#global n_sents
	#global n_token
	input_dir = "data/"
	input_file = input_dir+"url_overview.tsv"
	dataframe = pd.read_csv(input_file, sep="\t", header=0)
	# stanza.download('de')
	snlp = stanza.Pipeline('de', use_gpu=False)
	nlp = StanzaLanguage(snlp)
	filter = ("website", "bible_verified")
	do_stuff(dataframe, filter)
	# print(n_docs, n_sents, n_token)


if __name__ == "__main__":
	main()