# -*- coding: utf-8 -*-

import os, re, csv, requests, codecs
from pathlib import Path
import bs4
import urllib.request
from datetime import datetime

class AppURLopener(urllib.request.FancyURLopener):
	version = "Mozilla/5.0"



opener = AppURLopener()

def parse_overview_pages(page_url, output_dir, save_raw_content=False, save_only_parallel=True):
	if Path(output_dir+"url_overview.tsv").is_file():
		output = []
	else:
		output = [["website", "simple_url", "complex_url", "simple_level", "complex_level", "simple_location_html",
				   "complex_location_html", "simple_location_txt", "complex_location_txt", "alignment_location", "simple_author", "complex_author", "simple_title", "complex_title", "license", "last_access"]]

	#try:
	print("start:", page_url)
	if "apotheken-umschau" in page_url:
		tag = "apotheken-umschau"
		output.extend(parse_overview_apotheke(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	elif "hamburg.de" in page_url:
		tag = "stadt_hamburg"
		output.extend(parse_overview_hamburg(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	elif "taz.de" in page_url:
		tag = "taz"
		output.extend(parse_overview_taz(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	elif "stadt-koeln.de" in page_url:
		tag = "stadt_koeln"
		output.extend(parse_overview_koeln(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	elif "offene-bibel.de" in page_url and "in_Arbeit" in page_url:
		tag = "bible_working_progress"
		output.extend(parse_overview_bible(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	elif "offene-bibel.de" in page_url and "noch_zu_pr%C3%BCfen" in page_url:
		tag = "bible_awaiting_proof"
		output.extend(parse_overview_bible(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	elif "offene-bibel.de" in page_url and "Gepr%C3%BCfte_Leichte_Sprache" in page_url:
		tag = "bible_verified"
		output.extend(parse_overview_bible(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	# elif "https://www.evangelium-in-leichter-sprache.de/" in page_url:
	# 	tag = "bible_gospel"
	# 	output.extend(parse_overview_gospel(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir))
	elif "einfach-teilhaben.de" in page_url:
		tag = "einfach-teilhaben"
		output.extend(parse_overview_einfach_teilhaben(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel)[0])
	elif "os-hho.de" in page_url:
		tag = "os-hho"
		output.extend(parse_overview_os_hho(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	elif "lebenshilfe-main-taunus" in page_url:
		tag = "lebenshilfe_main_taunus"
		output.extend(parse_overview_lebenshilfe_main_taunus(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	elif "alumniportal-deutschland.org" in page_url:
		tag = "alumniportal-DE-2021"
		output.extend(parse_overview_alumniportal_2021(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
		# output.extend(parse_overview_alumniportal_2020(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir))
	elif "manual_alignment" in page_url:
		tag = "manual_alignment"
		output.extend(add_manual_aligned_urls(save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	elif "news-apa-xml" in page_url:
		tag = "news-apa-xml"
		output.extend(parse_overview_apa_xml(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	elif "science_apa_manual" in page_url:
		tag = "news-apa"
		output.extend(parse_overview_apa(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	elif "bzfe" in page_url and "einkaufen" in page_url:
		tag = "bzfe_einkaufen"
		output.extend(parse_overview_bzfe(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	elif "bzfe" in page_url and "kochen" in page_url:
		tag = "bzfe_kochen"
		output.extend(parse_overview_bzfe(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	elif "bzfe" in page_url and "essen" in page_url:
		tag = "bzfe_essen"
		output.extend(parse_overview_bzfe(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	elif "bzfe" in page_url and "familie" in page_url:
		tag = "bzfe_familie"
		output.extend(parse_overview_bzfe(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	elif "bpb.de" in page_url and "einfach" in page_url:
		tag = "einfach_politik"
		output.extend(parse_overview_bpb(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	elif "bpb.de" in page_url and "jung" in page_url:
		tag = "junge_politik"
		output.extend(parse_overview_bpb(page_url, tag, save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	else:
		tag = "else"
		list_simplified_urls, list_complex_urls = [], []
	#except:
	#	print("error")
	print("finished", tag, len(output))
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
	path_name = output_dir+"url_overview.tsv"
	with open(path_name, "a", newline="") as f:
		writer = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writer.writerows(output)
	return 1


def open_urls_safely(input_url):
	try:
		with opener.open(input_url) as url:
			soup_html = bs4.BeautifulSoup(url.read(), "lxml")
			return soup_html
	except ValueError:
		return None
		
	
def add_manual_aligned_urls(save_raw_content=False, output_dir="data/", save_only_parallel=True):
	output = list()
	output.extend(get_easy_to_read_books("links/books", "spaßamlesen_verlag", "citation required", save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	output.extend(get_easy_to_read_books("links/literature", "passanten_verlag", "citation required", save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	# output.extend(get_easy_to_read_books("links/fairytales", "fairytales", "not mentioned", save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	# output.extend(get_participation_urls("links/participation", save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	# output.extend(get_party_program("links/party_program", "party_program", "todo", save_raw_content=save_raw_content, output_dir=output_dir, save_only_parallel=save_only_parallel))
	return output


def get_easy_to_read_books(link, tag, license_name, save_raw_content=False, output_dir="data/", save_only_parallel=True):
	print(tag)
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title = "", "", "", "", "", "", "", "", "", ""
	access_date = datetime.today().strftime('%Y-%m-%d')
	with open(link + "_complex.txt") as f:
		complex_content = f.readlines()
	with open(link + "_simple.txt") as f:
		simple_content = f.readlines()
	complex_level = "C2"
	for i, simple_line in enumerate(simple_content):
		if i < len(complex_content):
			complex_title, complex_author, complex_level, complex_url = complex_content[i].strip().split("\t")
		else:
			complex_title, complex_author, complex_level, complex_url = "", "", "", ""
		simple_title, simple_author, simple_level, simple_url = simple_line.strip().split("\t")
		if save_raw_content:
			simple_location, complex_location, title_complex, title_complex = save_content(simple_url, complex_url, i, output_dir, tag, save_only_parallel)
		output.append([tag, simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
	return output


def get_party_program(link, tag, license_name, save_raw_content=False, output_dir="data/", save_only_parallel=True):
	print(tag)
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title = "", "", "", "", "", "", "", "", "", ""
	access_date = datetime.today().strftime('%Y-%m-%d')
	with open(link + "_complex.txt") as f:
		complex_content = f.readlines()
	with open(link + "_simple.txt") as f:
		simple_content = f.readlines()
	complex_level = "C2"
	i = 0
	for simple_line, complex_line in zip(simple_content, complex_content):
		simple_url, simple_level = simple_line.strip().split("\t")
		complex_url = complex_line.strip().split("\t")[0]
		if save_raw_content:
			simple_location, complex_location, simple_title, complex_title = save_content(simple_url, complex_url, i, output_dir, tag, save_only_parallel)
		output.append([tag, simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
		i += 1
	return output


def get_participation_urls(link, save_raw_content=False, output_dir="data/", save_only_parallel=True):
	tag = "participation"
	print(tag)
	output = list()
	i = 0
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title = "", "", "", "", "", "", "", "", "", ""
	access_date = datetime.today().strftime('%Y-%m-%d')
	with open(link + "_complex.txt") as f:
		complex_content = f.readlines()
	with open(link + "_simple.txt") as f:
		simple_content = f.readlines()
	for simple_url, complex_url in zip(simple_content, complex_content):
		if save_raw_content:
			simple_location, complex_location, simple_title, complex_title = save_content(simple_url, complex_url, i, output_dir, tag, save_only_parallel)
		output.append([tag, simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, "todo", access_date])
		i += 1
	return output


def get_complex_url_apotheke(soup):
	url_complex = ""
	paragraphs = soup.find_all("p", {"class": "text"})
	content = soup.find("article", {"class": ["article-detail"]})
	if not url_complex and paragraphs:
		for par_link in paragraphs:
			if par_link.text.strip().startswith("Sie wollen noch mehr über "):
				a_complex = par_link.find("a", {"title": "hier"}, href=True)
				if a_complex:
					url_complex = get_link(a_complex["href"], "https://www.apotheken-umschau.de")
	if not url_complex and content:
		link_more_info = content.find("a", {"type": "button"})
		if link_more_info:
			url_complex = get_link(link_more_info["href"], "https://www.apotheken-umschau.de")
	return url_complex


def get_complex_url_hamburg(soup):
	url_complex = ""
	list_a = soup.find_all("a", href=True)
	for link in list_a:
		if link.find("title") and "Alltagssprache" in link.find("title").text:
			url_complex = link["href"]
	return url_complex


def get_complex_url_taz(soup_simple_html):
	complex_urls = soup_simple_html.find_all("a", text=lambda x: x and "schwer" in x)
	if complex_urls:
		complex_url = "https://taz.de/" + complex_urls[0]["href"]
		return complex_url

	complex_p = soup_simple_html.find_all("p")
	for p in complex_p:
		if "Original" in p.text:
			complex_urls = p.find_all("a")
			if complex_urls:
				complex_url = "https://taz.de/" + complex_urls[0]["href"]
				return complex_url
	return ""


def get_complex_url_koeln(soup_simple_hmtl):
	complex_url = soup_simple_hmtl.find("a", text=lambda x: x and ("Diese Seite in Alltags-Sprache lesen" in x or "Diese Seite in  Alltags-Sprache lesen" in x))
	if complex_url:
		return complex_url["href"]
	else:
		return ""


def get_complex_url_einfach_teilhaben(simple_url):
	soup_complex = open_urls_safely(simple_url)
	if not soup_complex:
		return ""
	complex_url = soup_complex.find("a", {"class": "seitenumschaltung__tab__alltagssprache"})
	if complex_url:
		link = get_link("".join(complex_url["href"].partition(".html")[:-1]), "https://www.einfach-teilhaben.de/")
		return  link
	else:
		return ""


def get_complex_url(simple_url):
	url_complex = ""
	soup = open_urls_safely(simple_url)
	if not soup:
		return ""
	if "apotheken-umschau" in simple_url:
		url_complex = get_complex_url_apotheke(soup)
	elif "hamburg" in simple_url:
		url_complex = get_complex_url_hamburg(soup)
	# print("simple", simple_url, "complex", url_complex)
	return url_complex


def parse_overview_apotheke(overview_url, tag, save_raw_content=False, output_dir="data/", save_only_parallel=True):
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A2/B1", "C2"
	license_name = "copyright required"
	access_date = datetime.today().strftime('%Y-%m-%d')
	i = 0
	soup = open_urls_safely(overview_url)
	if not soup:
		return output
	content = soup.find("div", {"class": "linkliste"})
	if content:
		all_links = content.find_all("a")
		for link in all_links:
			simple_url = get_link(link["href"], "https://www.apotheken-umschau.de")
			try:
				complex_url = get_complex_url(simple_url)
			except OSError:
				print("reset by peer")
			if simple_url: #  and complex_url:
				if save_raw_content:
					simple_location, complex_location, simple_title, complex_title = save_content(simple_url, complex_url, i, output_dir, tag, save_only_parallel)
				output.append([tag, simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
				i += 1
	return output



def parse_overview_hamburg(overview_url, tag, save_raw_content=False, output_dir="data/", save_only_parallel=True):
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A1", "C2"
	license_name = "copyright reserved. dpa prohibited"
	access_date = datetime.today().strftime('%Y-%m-%d')
	i = 0
	soup = open_urls_safely(overview_url)
	if not soup:
		return output
	all_topics = soup.find_all("a", {"class": "topic-overview__link"})
	for topic in all_topics:
		topic_link = topic["href"]	
		soup_topic = open_urls_safely(topic_link)
		if not soup_topic:
			return output
		all_link_groups = soup_topic.find_all("div", {"class": "image-teaser-accessibility__bar"})
		for group in all_link_groups:
			all_links_of_group = group.find_all("a", {"class": "accessibility-item__content-link"})
			simple_url, complex_url = "", ""
			for link in all_links_of_group:
				if "Leichte Sprache" in link.text:
					simple_url = get_link(link["href"], "https://www.hamburg.de")
				elif "Original-Text" in link.text:
					complex_url = get_link(link["href"], "https://www.hamburg.de")
			if simple_url:  # and complex_url:
				if save_raw_content:
				 	simple_location, complex_location, simple_title, complex_title = save_content(simple_url, complex_url, i, output_dir, tag, save_only_parallel)
				output.append([tag, simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
				i += 1
	return output


def parse_overview_taz(overview_url, tag, save_raw_content=False, output_dir="data/", save_only_parallel=True):
	# in contrast to the urls, the simplified texts are build from one or more pages which makes the alignment more difficult
	output, post_list_simple_all = list(), list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A1", "C2"
	license_name = "copyright reserved, ask lizenzen@taz.de"
	access_date = datetime.today().strftime('%Y-%m-%d')
	soup = open_urls_safely(overview_url)
	if not soup:
		return output
	all_urls = soup.find_all("a", href= re.compile("^/Leichte-Sprache"))
	post_list_simple_all.extend(["https://taz.de/" + url["href"] for url in all_urls])
	i = 0
	for simple_url in post_list_simple_all:
		soup_simple_html = open_urls_safely(simple_url)
		if soup_simple_html:
			complex_url = get_complex_url_taz(soup_simple_html)
		# if complex_url:
		if save_raw_content:
			simple_location, complex_location, simple_title, complex_title = save_content(simple_url, complex_url, i, output_dir, tag, save_only_parallel)
		output.append([tag, simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
		i += 1
	# todo: multiple complex texts
	return output


def parse_overview_koeln(overview_url, tag, save_raw_content=False, output_dir="data/", save_only_parallel=True):
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A1", "C2"
	license_name = "written permit required"
	access_date = datetime.today().strftime('%Y-%m-%d')
	soup = open_urls_safely(overview_url)
	if not soup:
		return output
	all_lists = soup.find_all("ul", {"class": "textteaserliste"})
	i = 0
	for ul in all_lists:
		links_simple = ul.find_all("a")
		for simple_url in links_simple:
			simple_url_full = get_link(simple_url["href"], "https://www.stadt-koeln.de")
			soup_simple_html = open_urls_safely(simple_url_full)
			if soup_simple_html:
				complex_url = get_complex_url_koeln(soup_simple_html)
				if complex_url:
					complex_url = get_link(complex_url, "https://www.stadt-koeln.de")
			if save_raw_content:
				simple_location, complex_location, simple_title, complex_title = save_content(simple_url_full, complex_url, i, output_dir, tag, save_only_parallel)
			output.append([tag, simple_url_full, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
			i += 1
	return output


def parse_overview_bible(overview_url, tag, lexikon=False, save_raw_content=False, output_dir="data/", save_only_parallel=True):
	output, all_listings, lexikon_links = list(), list(), list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A1", "C2"
	license_name = "CC BY-SA 3.0"
	access_date = datetime.today().strftime('%Y-%m-%d')
	soup = open_urls_safely(overview_url)
	if not soup:
		return output
	all_lists = soup.find_all("ul", {"class": ""})
	for ul in all_lists:
		all_listings.extend(ul.find_all("li", {"class": ""}))
	if not lexikon:
		lexikon_links = parse_overview_bible("https://offene-bibel.de/wiki/Kategorie:Lexikon_in_Leichter_Sprache", lexikon=True, tag="lexikon")[0]
	i = 0
	for li in all_listings:
		simple_url = li.find("a")
		if simple_url and simple_url["href"].startswith("/wiki/") and \
				simple_url["href"] != "/wiki/Leichte_Sprache" and \
				simple_url["href"] != "/wiki/Bibel_in_Leichter_Sprache" and \
				simple_url["href"] != "/wiki/Was_ist_die_Bibel_in_Leichter_Sprache%3F" and \
				"https://offene-bibel.de"+simple_url["href"] not in lexikon_links:

			if simple_url["href"].endswith("_in_Leichter_Sprache") or simple_url["href"].endswith("_in_Leichter_Sprache_gepr%C3%BCft"):
				complex_url = simple_url["href"].split("_in_Leichter_Sprache")[0]
				if "," in complex_url:
					complex_url = complex_url.split(",")[0]
				if save_raw_content:
					simple_location, complex_location, simple_title, complex_title = save_content(get_link(simple_url["href"], "https://offene-bibel.de"), get_link(complex_url, "https://offene-bibel.de"), i, output_dir, tag, save_only_parallel)
				output.append([tag, get_link(simple_url["href"], "https://offene-bibel.de"), get_link(complex_url, "https://offene-bibel.de"), simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
				i += 1
	return output


def parse_overview_apa(overview_url, tag, lexikon=False, save_raw_content=False, output_dir="data/", save_only_parallel=True):
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A2", "B1"
	license_name = ""
	access_date = datetime.today().strftime('%Y-%m-%d')

	with open(overview_url) as f:
		content = f.read()
		soup = bs4.BeautifulSoup(content, 'html.parser')
	search_result = soup.find("div", {"class": "global-power-search__results"})
	all_items = search_result.find_all("a")
	i = 0
	for item in all_items:
		simple_url_full = get_link(item["href"], "https://science.apa.at")
		complex_url = simple_url_full
		if save_raw_content:
			simple_location, complex_location, simple_title, complex_title = save_content(simple_url_full, complex_url, i, output_dir, tag, save_only_parallel)
			output.append(
				[tag, simple_url_full, complex_url, simple_level, complex_level, simple_location, complex_location,
				 "", "", "", simple_author, complex_author, simple_title, complex_title, license_name, access_date])
			i += 1
	return output

def parse_overview_apa_xml(location, tag, lexikon=False, save_raw_content=False, output_dir="data/"):
	output = list()
	simple_level, complex_level = "A2", "B1"
	license_name = "contract"
	url = "https://science.apa.at/nachrichten-leicht-verstandlich/"
	access_date = "2021-04-20" # datetime.today().strftime('%Y-%m-%d')
	if save_raw_content:
		title = "data/news-apa-xml/itrp-239068_topeasy.xml", "Nachrichten leicht verständlich"
		output.append(
			[tag, url, url, simple_level, complex_level, location, location,
			 "", "", "", "APA - Austria Presse Agentur eG", "APA - Austria Presse Agentur eG", title, title, license_name, access_date])
	return output


# def parse_overview_gospel(overview_url, tag, save_raw_content=False, output_dir="data/"):
#
# 	output, all_listings, all_titles, lexikon_links = list(), list(), list(), list()
# 	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
# 	simple_level, complex_level = "A1", "C2"
# 	license_name = "CC BY-NC-SA 4.0"
# 	access_date = datetime.today().strftime('%Y-%m-%d')
# 	with opener.open(overview_url) as url:
# 		soup = bs4.BeautifulSoup(url.read(), "lxml")
# 	next_page = soup.find("a", {"title": "Zur nächsten Seite"})
# 	i = 0
# 	while next_page:
# 		print(next_page["href"])
# 		container = soup.find("div", {"class": "view-content"})
# 		listings_one_page = container.find_all("a")
# 		for listing in listings_one_page:
# 			simple_url = listing["href"]
# 			simple_title = listing.text
# 			if simple_url:
# 				name, number = simple_title.split(",")[0].split(" ")
# 				complex_url = "https://offene-bibel.de/wiki/"+name+"_"+number
# 			if save_raw_content:
# 				simple_location, complex_location, simple_title, complex_title = save_content(get_link(simple_url, "https://www.evangelium-in-leichter-sprache.de"), get_link(complex_url, "https://offene-bibel.de"), i, output_dir, tag)
# 			output.append([tag, get_link(simple_url, "https://www.evangelium-in-leichter-sprache.de"), get_link(complex_url, "https://offene-bibel.de"), simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
# 			i += 1
# 		with opener.open(get_link(next_page["href"], "https://www.evangelium-in-leichter-sprache.de/")) as url:
# 			soup = bs4.BeautifulSoup(url.read(), "lxml")
# 		next_page = soup.find("a", {"title": "Zur nächsten Seite"})
# 	return output


def check_subpage(url, element, attribute, attribute_value):
	soup = open_urls_safely(url)
	if not soup:
		return []
	else:
		all_lists = soup.find_all(element, {attribute: attribute_value})
		return all_lists


def parse_overview_einfach_teilhaben(overview_page, tag, save_raw_content=False, output_dir="data/", i=0, save_only_parallel=True):
	# @todo: consider that subpages can also have content and sublinks, e.g. https://www.einfach-teilhaben.de/DE/LS/Themen/LiebeSexualitaet/Familienplanung/Familienplanung_node.html
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	all_lists = check_subpage(overview_page, "li", "class", "themen__teaser__container")
	simple_level, complex_level = "A1", "C2"
	license_name = "nothing regarding texts mentioned"
	access_date = datetime.today().strftime('%Y-%m-%d')
	# print(all_lists)
	if len(all_lists) > 0:
		for listing in all_lists:
			link = get_link("".join(listing.find("a")["href"].partition(".html")[:-1]), "https://www.einfach-teilhaben.de/")
			# print(i,link)
			subpages, i = parse_overview_einfach_teilhaben(link, tag, save_raw_content=save_raw_content, output_dir=output_dir, i=i)
			if type(subpages) == list:
				output.extend(subpages)
			else:
				complex_url = get_complex_url_einfach_teilhaben(subpages)
				# if complex_url:
				if save_raw_content:
					simple_location, complex_location, simple_title, complex_title = save_content(subpages, complex_url, i, output_dir, tag, save_only_parallel)
				output.append([tag, subpages, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
				i += 1
		return output, i
	else:
		return overview_page, i


def get_link(link, url):
	if link.startswith(url):
		return link
	if link.startswith(url.replace("https", "http")):
		return link
	else:
		return url+link


def parse_overview_os_hho(overview_page, tag, save_raw_content=False, output_dir="data/", save_only_parallel=True):
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A2/B1", "C2"
	license_name = "copyright reserved"
	post_list_simple, post_list_complex = list(), list()
	access_date = datetime.today().strftime('%Y-%m-%d')
	soup = open_urls_safely(overview_page)
	if not soup:
		return output
	all_urls = set()
	i = 0
	for url_tag in soup.find_all("a"):
		url = url_tag["href"]
		if not url.endswith(".pdf") and url not in all_urls \
				and	(url.startswith("https://www.os-hho.de") or url.startswith("/")) \
				and not url.endswith("#content") and not url.endswith("#hauptnavigation"):
			all_urls.add(get_link(url, "https://www.os-hho.de"))
			for simple_url in check_subpage(get_link(url, "https://www.os-hho.de"), "a", "title",
												  "Klicken Sie hier, um sich den Text in einfacher Sprache anzeigen zu lassen"):
				if get_link(simple_url["href"], "https://www.os-hho.de") not in post_list_simple:
					post_list_simple.append(get_link(simple_url["href"], "https://www.os-hho.de"))
					if save_raw_content:
						simple_location, complex_location, simple_title, complex_title = save_content(get_link(simple_url["href"], "https://www.os-hho.de"), get_link(url, "https://www.os-hho.de"), i, output_dir, tag, save_only_parallel)
					output.append([tag, get_link(simple_url["href"], "https://www.os-hho.de"), get_link(url, "https://www.os-hho.de"), simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
					i += 1
	return output


def parse_overview_lebenshilfe_main_taunus(overview_page, tag, save_raw_content=False, output_dir="data/", save_only_parallel=True):
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	soup = open_urls_safely(overview_page)
	if not soup:
		return output
	div_ul = soup.find("div", {"id": "inhalt_sitemap"})
	all_urls = list({get_link(url.find("a")["href"], "https://www.lebenshilfe-main-taunus.de") for url in div_ul.find_all("li")})
	simple_level, complex_level = "A1", "C2"
	license_name = "permit required"
	access_date = datetime.today().strftime('%Y-%m-%d')
	i = 0
	for complex_url in all_urls:
		try:
			with opener.open(complex_url) as url:
				soup_complex_url = bs4.BeautifulSoup(url.read(), "lxml")
		except UnicodeError:
			continue
		simple_element = soup_complex_url.find("img", title="Auf Leichte Sprache umstellen").parent
		if simple_element.name == "a" and simple_element["href"] != "/ls/" and not re.search(r"/ls/-\d{3}\.html", simple_element["href"]):
			simple_url = get_link(simple_element["href"], "https://www.lebenshilfe-main-taunus.de")
			if save_raw_content:
				simple_location, complex_location, simple_title, complex_title = save_content(simple_url, complex_url, i, output_dir, tag, save_only_parallel)
			output.append([tag, simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
			i += 1
	return output


def parse_overview_alumniportal_2021(page_url, tag, save_raw_content=False, output_dir="data/", save_only_parallel=True):
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A2", "B2"
	license_name = "CC BY 4.0"
	access_date = datetime.today().strftime('%Y-%m-%d')
	soup = open_urls_safely(page_url)
	if not soup:
		return output
	# head_listing = soup.find_all("a", href = re.compile("^deutsche-sprache/deutsch-auf-die-schnelle/.+"))
	"https://www.alumniportal-deutschland.org/digitales-lernen/deutsche-sprache/lesetexte/lesetexte-sprachniveau-a1-a2/"
	"https://www.alumniportal-deutschland.org/digitales-lernen/deutsche-sprache/lesetexte/b1-b2/online-deutsch-lernen-uebungen-integration-b/"
	"digitales-lernen/deutsche-sprache/lesetexte/lesetexte-sprachniveau-a1-a2/"
	simple_part = "lesetexte/lesetexte-sprachniveau-a1-a2/"
	complex_part = "lesetexte/b1-b2/"
	head_listing = soup.find_all("a", href=re.compile("^/digitales-lernen/deutsche-sprache/lesetexte/lesetexte-sprachniveau-a1-a2/.+"))
	head_listing_complex = soup.find_all("a", href=re.compile("^/digitales-lernen/deutsche-sprache/lesetexte/b1-b2/.+"))
	i = 0
	head_listing = [get_link(link["href"], "https://www.alumniportal-deutschland.org") for link in head_listing if "online-deutsch-lernen-uebungen-" in link["href"]]
	head_listing_complex = [get_link(link["href"], "https://www.alumniportal-deutschland.org") for link in head_listing_complex if "online-deutsch-lernen-uebungen-" in link["href"]]
	if head_listing:
		for link in head_listing:
			simple_url = link
			complex_candidate = simple_url.replace(simple_part, complex_part)
			if complex_candidate.endswith("-a"):
				complex_candidate = complex_candidate[:-1]+"b"
			elif complex_candidate.endswith("-a1-a2"):
				complex_candidate = complex_candidate[:-5]+"b1-b2"
			if complex_candidate in head_listing_complex:
				complex_url = complex_candidate
			# if complex_url and simple_url:
			if save_raw_content:
				simple_location, complex_location, simple_title, complex_title = save_content(simple_url, complex_url,
																							  i, output_dir, tag, save_only_parallel)
			output.append(
				[tag, simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, "", "",
				 "", simple_author, complex_author, simple_title, complex_title, license_name, access_date])
			i += 1
	return output


def parse_overview_alumniportal_2020(page_url, tag, save_raw_content=False, output_dir="data/", save_only_parallel=True):
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A2", "B2"
	license_name = "CC BY 4.0"
	access_date = datetime.today().strftime('%Y-%m-%d')
	soup = open_urls_safely(page_url)
	if not soup:
		return output
	# head_listing = soup.find_all("a", href = re.compile("^deutsche-sprache/deutsch-auf-die-schnelle/.+"))
	head_listing = soup.find_all("a", href=re.compile("^digitales-lernen/deutsche-sprache/deutsch-auf-die-schnelle/.+"))
	i = 0
	if head_listing:
		for link in head_listing:
			simple_url, complex_url = get_link(link["href"], "https://www.alumniportal-deutschland.org/"), get_link(link["href"], "https://www.alumniportal-deutschland.org/")
			if save_raw_content:
				simple_location, complex_location, simple_title, complex_title = save_content(simple_url, complex_url, i, output_dir, tag, save_only_parallel)
			output.append([tag, simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
			i += 1
	return output

def parse_overview_bpb_complex(overview_url):
	complex_dict = dict()
	soup = open_urls_safely(overview_url)
	if not soup:
		return complex_dict
	group_per_letter = soup.find_all("li", {"class": "topic-container__item"})
	for letter_group in group_per_letter:
		all_links = letter_group.find_all("a", {"class": "topic-list__link"})
		for link in all_links:
			complex_dict[link.text.strip()] = get_link(link["href"], "https://www.bpb.de")

	return complex_dict
	
def get_all_bpb_links(overview_url):
	soup = open_urls_safely(overview_url)
	if not soup:
		return []
	else:
		all_urls = soup.find_all("a", {"class": "topic-list__link"})
		return all_urls

def parse_overview_bpb(overview_url, tag, save_raw_content=False, output_dir="data/", save_only_parallel=True):
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A2/B1", "C2"
	license_name = "CC BY-NC-ND 3.0 DE"
	access_date = datetime.today().strftime('%Y-%m-%d')
	i = 0
	all_urls = get_all_bpb_links(overview_url)
	# "Jane Baer-Krause, Anette Bäßler, Christiane Baumann, Oliver Boyn, Peter Brandt, Danielle Cohn, Stefan Eling, Tanja Hebenstreit, Claudia Hennerkes, Katharina Hoba, Lamya Kaddor, Kristine Kretschmer, Claudia Nölling-Schweers, Catherine Raoult, Katharina Reinhold, Katrin Rosenthal, Verena Sauvage, Renate Schindler, Gerd Schneider, Anja Stöcker, Christiane Toyka-Seid und Thomas Werner"
	complex_dict = parse_overview_bpb_complex("https://www.bpb.de/kurz-knapp/lexika/politiklexikon/")
	for simple_link in all_urls:
		simple_url = get_link(simple_link["href"], "https://www.bpb.de")
		if save_raw_content:
			if simple_link.text.strip() in complex_dict.keys():
				complex_link = get_link(complex_dict[simple_link.text.strip()], "https://www.bpb.de")
			else:
				complex_link = ""
				complex_location = ""
				complex_title = ""
			# if simple_link and complex_link:
			simple_location, complex_location, simple_title, complex_title = save_content(simple_url, complex_link, i, output_dir, tag, save_only_parallel)
			# else:
			# 	simple_location, complex_location, simple_title, complex_title = "", "", "", ""
		output.append([tag, simple_url, complex_link, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
		i += 1
	return output

def parse_overview_bzfe(overview_url, tag, save_raw_content=False, output_dir="data/", save_only_parallel=True):
	output = list()
	simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, simple_author, complex_author, simple_title, complex_title, license_name = "", "", "", "", "", "", "", "", "", "", ""
	simple_level, complex_level = "A2/B1", "C2"
	license_name = "CC BY-NC-ND 4.0"
	access_date = datetime.today().strftime('%Y-%m-%d')
	i = 0
	soup = open_urls_safely(overview_url)
	if not soup:
		return output
	overview = soup.find("div", {"class": "module-teaserlist"})
	all_urls = list({get_link(url["href"], "https://www.bzfe.de") for url in overview.find_all("a", title=True)})
	for simple_link in all_urls:
		#parent = post.parent.parent
		#grandparent = post.parent.parent.parent.parent.parent.parent
		# link_complex = get_complex_url_bzfe(grandparent)
		#if parent["href"] and link_complex:
		if save_raw_content:
			simple_complex_dict = {"https://www.bzfe.de/einfache-sprache/zubereitung/": "https://www.bzfe.de/lebensmittel/zubereitung/lebensmittel-garen/", "https://www.bzfe.de/einfache-sprache/wenn-kinder-kein-gemuese-essen/": "https://www.bzfe.de/ernaehrung/ernaehrungswissen/in-bestimmten-lebensphasen/wenn-kinder-kein-gemuese-moegen/", "https://www.bzfe.de/einfache-sprache/verpackungsmuell-vermeiden/": "https://www.bzfe.de/nachhaltiger-konsum/orientierung-beim-einkauf/verpackungsmuell-vermeiden/", "https://www.bzfe.de/einfache-sprache/vegan-essen/": "https://www.bzfe.de/lebensmittel/trendlebensmittel/vegane-lebensmittel/", "https://www.bzfe.de/einfache-sprache/schnelle-kueche/": "https://www.bzfe.de/nachhaltiger-konsum/lagern-kochen-essen-teilen/fertigprodukte-selber-machen/", "https://www.bzfe.de/einfache-sprache/portionsgroessen/": "https://www.bzfe.de/ernaehrung/die-ernaehrungspyramide/die-ernaehrungspyramide-eine-fuer-alle/ernaehrungspyramide-wie-gross-ist-eine-portion/", "https://www.bzfe.de/einfache-sprache/meal-prepping/": "https://www.bzfe.de/nachhaltiger-konsum/lagern-kochen-essen-teilen/meal-prepping/", "https://www.bzfe.de/einfache-sprache/lagerung/": "https://www.bzfe.de/nachhaltiger-konsum/lagern-kochen-essen-teilen/lebensmittel-richtig-lagern/", "https://www.bzfe.de/einfache-sprache/klimatipps/": "https://www.bzfe.de/nachhaltiger-konsum/orientierung-beim-einkauf/ernaehrung-und-klimaschutz/", "https://www.bzfe.de/einfache-sprache/haltbarkeit/": "https://www.bzfe.de/service/news/aktuelle-meldungen/news-archiv/meldungen-2018/maerz/haltbarkeit-von-lebensmitteln/", "https://www.bzfe.de/einfache-sprache/fertigprodukte/": "https://www.bzfe.de/lebensmittel/einkauf-und-kennzeichnung/convenience/convenience-produkte-im-alltag/", "https://www.bzfe.de/einfache-sprache/essen-und-stress/": "https://www.bzfe.de/ernaehrung/ernaehrungswissen/gesundheit/wie-emotionen-unser-essen-beeinflussen/", "https://www.bzfe.de/einfache-sprache/essen-in-schule-und-kita/": "https://www.bzfe.de/bildung/lernort-schule-und-kita/das-pausenbrot-unter-der-lupe/", "https://www.bzfe.de/einfache-sprache/essen-im-alter/": "https://www.bzfe.de/ernaehrung/ernaehrungswissen/in-bestimmten-lebensphasen/ue60-das-beste-alter/", "https://www.bzfe.de/einfache-sprache/energy-drinks/": "https://www.bzfe.de/lebensmittel/trendlebensmittel/energydrinks/", "https://www.bzfe.de/einfache-sprache/die-ernaehrungspyramide-1/": "https://www.bzfe.de/ernaehrung/die-ernaehrungspyramide/die-ernaehrungspyramide-eine-fuer-alle/", "https://www.bzfe.de/einfache-sprache/der-saisonkalender/": "https://www.bzfe.de/nachhaltiger-konsum/orientierung-beim-einkauf/der-saisonkalender/saisonzeiten-bei-obst-und-gemuese/", "https://www.bzfe.de/einfache-sprache/allergenkennzeichnung/": "https://www.bzfe.de/lebensmittel/einkauf-und-kennzeichnung/kennzeichnung/allergenkennzeichnung/"}
			if simple_link in simple_complex_dict.keys():
				complex_link = simple_complex_dict[simple_link]
			else:
				complex_link = ""
				complex_location = ""
				complex_title = ""
			if simple_link:  # and complex_link:
				simple_location, complex_location, simple_title, complex_title = save_content(simple_link, complex_link, i, output_dir, tag, save_only_parallel)
			# else:
			# 	simple_location, complex_location, simple_title, complex_title = "", "", "", ""
		output.append([tag, simple_link, complex_link, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, license_name, access_date])
		i += 1
	return output

def save_non_parallel_books(book_list_simple, output, output_dir, tag, save_only_parallel):
	save_only_parallel = False
	output = list()
	i = 0
	access_date = datetime.today().strftime('%Y-%m-%d')
	for simple_item in book_list_simple:
		simple_title, simple_author, simple_level, simple_url = simple_item
		simple_location, complex_location, simple_title, complex_title = save_content(simple_url, "", i, output_dir, tag, save_only_parallel)
		output.append([tag, simple_url, "", simple_level, "", simple_location, "", "", "", "",  simple_author, "", simple_title, "", "to_add", access_date])
		i += 1
	return output
	

def save_parallel_books(book_list_simple, book_list_complex, output, output_dir, tag, save_only_parallel):
	save_only_parallel = False
	output = list()
	i = 0
	access_date = datetime.today().strftime('%Y-%m-%d')
	for simple_item, complex_item in zip(book_list_simple, book_list_complex):
		complex_title, complex_author, complex_level, complex_url = complex_item
		simple_title, simple_author, simple_level, simple_url = simple_item
		simple_location, complex_location, title_complex, title_complex = save_content(simple_url, complex_url, i, output_dir, tag, save_only_parallel)
		output.append([tag, simple_url, complex_url, simple_level, complex_level, simple_location, complex_location, "", "", "",  simple_author, complex_author, simple_title, complex_title, "to_add", access_date])
		i += 1
	return output


def umlauts_coverter_for_url(link):
	if "ä" in link:
		return link.replace("ä", "%C3%A4")
	if "ü" in link:
		return link.replace("ä", "%C3%BC")
	if "ö" in link:
		return link.replace("ä", "%C3%B6")
	else:
		return link


def save_html(level, output_dir, sub_dir, save_type, i, link):
	title = ""
	try:
		soup = open_urls_safely(umlauts_coverter_for_url(link))
		if not soup or not soup.head:
			return "", ""
		comment = bs4.Comment('&copy; Origin: ' + link + " [last accessed: " + datetime.today().strftime('%Y-%m-%d') + "]")
		soup.head.insert(-1, comment)
		title = soup.find("title")
		if title:
			title = title.string
		with open(output_dir + sub_dir + save_type + "/" + level + str(i) + '.html', "w") as file:
			file.write(str(soup))
	except (ValueError, ConnectionResetError, OSError):
		print(link, "not accessible")
		return "", ""
	return output_dir + sub_dir + save_type + "/" + level + str(i) + '.html', title


def save_pdf(level, output_dir, sub_dir, save_type, i, link):
	r = requests.get(link, stream=True)

	with open(output_dir + sub_dir + save_type + "/" + level + str(i) + '.pdf', "wb") as pdf:
		for chunk in r.iter_content(chunk_size=1024):
			if chunk:
				pdf.write(chunk)
	return output_dir + sub_dir + save_type + "/" + level + str(i) + '.pdf'


def save_content(simple_link, complex_link, i, output_dir, sub_dir, save_only_parallel=True):
	sub_dir = sub_dir+"/"
	if not os.path.exists(output_dir+sub_dir):
		os.makedirs(output_dir+sub_dir)
	if not simple_link.endswith("pdf") and not os.path.exists(output_dir+sub_dir+"html/"):
		os.makedirs(output_dir+sub_dir+"html/")
	if not complex_link.endswith("pdf") and not os.path.exists(output_dir+sub_dir+"html/"):
		os.makedirs(output_dir+sub_dir+"html/")
	if not simple_link.endswith("pdf") and not save_only_parallel and not os.path.exists(output_dir+sub_dir+"only_simple_html/"):
		os.makedirs(output_dir+sub_dir+"only_simple_html/")
	elif simple_link.endswith("pdf") and not os.path.exists(output_dir+sub_dir+"pdf/"):
		os.makedirs(output_dir+sub_dir+"pdf/")
	elif complex_link.endswith("pdf") and not os.path.exists(output_dir+sub_dir+"pdf/"):
		os.makedirs(output_dir+sub_dir+"pdf/")
	elif simple_link.endswith("pdf") and not save_only_parallel and not os.path.exists(output_dir+sub_dir+"only_simple_pdf/"):
		os.makedirs(output_dir+sub_dir+"only_simple_pdf/")

	simple_location, complex_location, simple_title, complex_title = "", "", "", ""
	if simple_link and complex_link:
		if not simple_link.endswith("pdf"):
			simple_location, simple_title = save_html("simple_", output_dir, sub_dir, "html", i, simple_link)
		elif simple_link.endswith("pdf"):
			simple_location = save_pdf("simple_", output_dir, sub_dir, "pdf", i, simple_link)
		if not complex_link.endswith("pdf"):
			complex_location, complex_title = save_html("complex_", output_dir, sub_dir, "html", i, complex_link)
		elif complex_link.endswith("pdf"):
			complex_location = save_pdf("complex_", output_dir, sub_dir, "pdf", i, complex_link)

	elif simple_link and not save_only_parallel:
		if not simple_link.endswith("pdf"):
			simple_location, simple_title = save_html("simple_", output_dir, sub_dir, "only_simple_html", i, simple_link)
		elif simple_link.endswith("pdf"):
			simple_location = save_pdf("simple_", output_dir, sub_dir, "only_simple_pdf", i, simple_link)
	return simple_location, complex_location, simple_title, complex_title


def main():
	output_dir = "data/"
	save_raw_content = True
	save_only_parallel = False

	if not os.path.exists(output_dir):
		os.makedirs(output_dir)


	overview_pages = [
					"https://www.alumniportal-deutschland.org/services/sitemap/",
					"https://www.lebenshilfe-main-taunus.de/inhalt/",
					## "https://www.os-hho.de/",
					"https://www.einfach-teilhaben.de/DE/LS/Home/leichtesprache_node.html",

					"https://offene-bibel.de/wiki/Kategorie:Leichte_Sprache_in_Arbeit",
					"https://offene-bibel.de/wiki/Kategorie:Leichte_Sprache_noch_zu_pr%C3%BCfen",
					"https://offene-bibel.de/wiki/Kategorie:Gepr%C3%BCfte_Leichte_Sprache",

					"https://www.stadt-koeln.de/leben-in-koeln/soziales/informationen-leichter-sprache",
					"https://taz.de/leicht/!p5097//",
					"https://www.apotheken-umschau.de/einfache-sprache/",
					"https://www.hamburg.de/hamburg-barrierefrei/leichte-sprache/",
					"https://www.bzfe.de/einfache-sprache/einkaufen/",
					"https://www.bzfe.de/einfache-sprache/kochen-aufbewahren/",
					"https://www.bzfe.de/einfache-sprache/gut-essen/", 
					"https://www.bzfe.de/einfache-sprache/familie/",
					"https://www.bpb.de/nachschlagen/lexika/lexikon-in-einfacher-sprache/",
					"https://www.bpb.de/nachschlagen/lexika/das-junge-politik-lexikon/", 
					"manual_alignment"

					# NEW
					#"https://www.evangelium-in-leichter-sprache.de/bibelstellen",
					#"https://www.bildung.bremen.de/informationen_in_leichter_sprache-17528",
					#"https://www.gesundheit.bremen.de/service/informationen_in_leichter_sprache-20060",
					#"https://www.wirtschaft.bremen.de/information_in_leichter_sprache-10108",
					#"https://www.gesundheit.bremen.de/service/informationen_in_leichter_sprache-20060",
					#"https://www.wissenschaft-haefen.bremen.de/information_in_leichter_sprache-10108",
					#"https://www.lis.bremen.de/ueber_das_lis/informationen_in_leichter_sprache-84242",
					#"http://www.on-line-on.eu/",
					#"https://www.bmwi.de/Navigation/DE/Service/Leichte-Sprache/leichte-sprache.html",
					#"https://www.bmjv.de/DE/LeichteSprache/Leichte_Sprache_node.html",
					#"https://www.bmas.de/DE/Leichte-Sprache/leichte-sprache.html"
					#"data/news-apa-xml/itrp-239068_topeasy.xml"
					#"data/science_apa_manual/Search.html"
					# "https://www.bzfe.de/einfache-sprache/"
					]

	#
	# https://www.lebenshilfe-wiesbaden.de/index.php
	# https://www.lebenshilfe-duesseldorf.de/index.php?id=78

	for overview in overview_pages:
		parse_overview_pages(overview, output_dir, save_raw_content=save_raw_content, save_only_parallel=save_only_parallel)
	return 1


if __name__ == "__main__":
	main()
