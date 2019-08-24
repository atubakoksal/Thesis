#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import codecs
from bs4 import BeautifulSoup
import abbreviations
import sys

def extract_html(filename):
	# Keep a global dictionary for abbreviations
	abbrv_dict = {}
	with open(filename) as file:
	    soup = BeautifulSoup(file, 'lxml')

	outtext = codecs.open(filename[:-5]+".txt", "w", "utf-8")

	a_tag = soup.findAll(['a', 'sup'])

	stopTitles = ["Acknowledgments", "ACKNOWLEDGMENT","Acknowledgements", "Acknowledgment", "Abbreviations", \
		"Availability of data and materials", "Authors’ contributions", "Author Contributions", \
		"Contributor Information", "Corresponding Author", "References", "Bibliography", \
		"Supplementary Material"]

	for match in a_tag:
		match.decompose()

	try:
		for data in soup.findAll('div', {'class': 'tsec sec'}):
			for i in data.findAll(['h2','p']):
				if i.text.encode('UTF-8') in stopTitles:
					raise Exception
				else:
					outtext.write("\n")					
					s = ""
					for i in i.text.splitlines():
						s += i.strip() + " "
					# Update the abbreviations dictionary
					abbrv_dict.update(abbreviations.abbrv_text(s))
					# Clean the paranthesis
					s = re.sub(r'(\(.*?\)|\[.*?\]|[\(\)\)])', '', s)
					# Search and replace the abbreviations
					# (case insensitive)
					for cand, defn in abbrv_dict.items():
						s = re.sub(cand, defn, s)
					outtext.write(s)
	except:
		pass
	
	# Prints the abbreviations
	# (For debugging purposes)
	for i, j in abbrv_dict.items():
		print i, j

	outtext.close()

if __name__ == "__main__":
	filename = sys.argv[1]
	extract_html(filename)
	print "Your file saved as " + filename[:-5]+".txt"


