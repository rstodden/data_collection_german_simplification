# -*- coding: utf-8 -*-

import os
import spacy
import pandas as pd

source_dict = {"apotheken-umschau": {"simple": "B1", "complex": "C2", "domain": "biomed", "license": 0.75, "language": "DE"}, 
		"bible_awaiting_proof": {"simple": "A1", "complex": "C2", "domain": "bible", "license": 1, "language": "DE"},
		"bible_working_progress": {"simple": "A1", "complex": "C2", "domain": "bible", "license": 1, "language": "DE"},
		"bible_verified": {"simple": "A1", "complex": "C2", "domain": "bible", "license": 1, "language": "DE"},
		"DE-geolino.test.src": {"simple": "children_8-14", "complex": "", "domain": "general-interest magazine", "license": 1, "language": "DE"},
		"DE-geolino.valid.src": {"simple": "children_8-14", "complex": "", "domain": "general-interest magazine", "license": 1, "language": "DE"},
		"DE-geolino.test.tgt": {"simple": "children_5-7", "complex": "", "domain": "general-interest magazine", "license": 1, "language": "DE"},
		"DE-geolino.valid.tgt": {"simple": "children_5-7", "complex": "", "domain": "general-interest magazine", "license": 1, "language": "DE"},
		"DE-klexi_corpus.json": {"simple": "children_6-12", "complex": "", "domain": "wiki", "license": 1, "language": "DE"},
		"DE-miniklexi_corpus.json": {"simple": "children reading beginners", "complex": "", "domain": "wiki", "license": 1, "language": "DE"},
		"DE-wiki_corpus.json": {"simple": "", "complex": "C2", "domain": "wiki", "license": 1, "language": "DE"},
		"news-apa-xml": {"simple": "A2", "complex": "B2", "domain": "news", "license": 1, "language": "DE"},
		"DE-APA_LHA": {"A2-OR": {"simple": "A2", "complex": "C2", "domain": "news", "license": 1, "language": "DE"},
				"B1-OR": {"simple": "B1", "complex": "C2", "domain": "news", "license": 1, "language": "DE"},
				},
		"passanten-verlag": {"simple": "A2/B1", "complex": "C2", "domain": "fiction", "license": 0.75, "language": "DE"},
		"spaß-am-lesen-verlag": {"simple": "A2/B1", "complex": "C2", "domain": "fiction", "license": 1, "language": "DE"},
		"bzfe_kochen": {"simple": "A2/B1", "complex": "C2", "domain": "health/food", "license": 1, "language": "DE"},
		"bzfe_einkaufen": {"simple": "A2/B1", "complex": "C2", "domain": "health/food", "license": 1, "language": "DE"},
		"bzfe_familie": {"simple": "A2/B1", "complex": "C2", "domain": "health/food", "license": 1, "language": "DE"},
		"bzfe_essen": {"simple": "A2/B1", "complex": "C2", "domain": "health/food", "license": 1, "language": "DE"},
		"alumniportal-DE-2020": {"simple": "A2", "complex": "B2", "domain": "language learner", "license": 1, "language": "DE"},
		"alumniportal-DE-2020": {"simple": "A2", "complex": "B2", "domain": "language learner", "license": 1, "language": "DE"},
		"junge_politik": {"simple": "children_6", "complex": "C2", "domain": "politics", "license": 0.75, "language": "DE"},
		"einfach_politik": {"simple": "A2/B1", "complex": "C2", "domain": "politics", "license": 0.75, "language": "DE"},
		"einfach-teilhaben": {"simple": "A1", "complex": "C2", "domain": "web", "license": 0.75, "language": "DE"},
		"stadt_koeln": {"simple": "A1", "complex": "C2", "domain": "web", "license": 0.75, "language": "DE"},
		"stadt_hamburg": {"simple": "A1", "complex": "C2", "domain": "web", "license": 0.75, "language": "DE"},
		}

def add_data(output_data, file_list, dir_path, name, level):
	i = len(output_data)
	for file_path in file_list:
		print(dir_path+file_path)
		with open(dir_path+file_path, "r", encoding="utf-8") as f:
			document_content = f.readlines()
		if len(document_content) <= 1:
			continue
		copyright_line, title = document_content[0].strip().split("\t")
		copyright_line = copyright_line.split(" ")
		date = copyright_line[-1][:-1]
		url = " ".join(copyright_line[3:-3])
		file_nr = file_path.split("_")[-1].split(".")[0]
		if name in source_dict.keys():
			detailed_level = source_dict[name][level]
			domain = source_dict[name]["domain"]
			size = source_dict[name]["license"]
			language = source_dict[name]["language"]
		else:
			detailed_level = ""
			domain = ""
			size = 1
			language = ""
		sentences = list(nlp(document_content[1].strip()).sents)
		sentences = sentences[:round(len(sentences)*size)]
		for sent in sentences:
			if len(sent) > 2:
				output_data.loc[i] = [sent, level, detailed_level, language, url, title, date, domain, name, file_nr]
				i += 1
	return output_data

def select_files_and_add_data(full_dir_path, dir_path, output_data):
	if not os.path.isdir(full_dir_path):
		return  output_data
	simple_files = [file_path for file_path in os.listdir(full_dir_path) if "simple_" in file_path]
	complex_files = [file_path for file_path in os.listdir(full_dir_path) if "complex_" in file_path]
	output_data = add_data(output_data, simple_files, full_dir_path, dir_path, "simple")
	output_data = add_data(output_data, complex_files, full_dir_path, dir_path, "complex")
	return output_data


nlp = spacy.load("de_dep_news_trf")
output_data = pd.DataFrame(columns=["text", "level", "detailed_level", "language", "url", "title", "date", "domain", "source", "file_nr"])

i = 0
for dir_path in os.listdir("data/"):
	print(dir_path+"/txt/", os.path.isdir("data/"+dir_path+"/txt/"))
	if dir_path == "books_einfachebücher":
		full_dir_path = "data/"+dir_path+"/passanten-verlag/"
		output_data = select_files_and_add_data(full_dir_path, "passanten-verlag", output_data)
		full_dir_path = "data/"+dir_path+"/spaß-am-lesen-verlag/"
		output_data = select_files_and_add_data(full_dir_path, "spaß-am-lesen-verlag", output_data)
	else:
		full_dir_path = "data/"+dir_path+"/txt/"
		output_data = select_files_and_add_data(full_dir_path, dir_path, output_data)

	output_data.to_csv("data/DE_textlevel_webdata.csv", index=False)
output_data = output_data.drop_duplicates()		
output_data.to_csv("data/DE_textlevel_webdata_clean.csv", index=False)
			

