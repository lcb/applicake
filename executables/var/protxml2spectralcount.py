#!/usr/bin/env python

import sys
import csv
import argparse
import xml.etree.ElementTree as ET

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-CSV', help='peptides tsv from pepxml2csv')
	parser.add_argument('-TYP', help='peptides to count',choices=['all','unique'],default='all')
	parser.add_argument('-OUT', help='outfile')
	parser.add_argument('PROT', help='prot XML')
	args = parser.parse_args()

	print "PARSING",args.CSV
	peptides_samples = {}
	tsvreader = csv.DictReader(open(args.CSV,'r'), delimiter='\t')
	for line in tsvreader:
		pep = line['peptide']
		sample = line['spectrum'].split(".")[0]
		lst = peptides_samples.get(pep,[])
		lst.append(sample)
		peptides_samples[pep] = lst

	print "PARSING AND UPDATING",args.PROT
	ET.register_namespace('', "http://regis-web.systemsbiology.net/protXML")
	root = ET.parse(args.PROT).getroot()
	for protein in root.iter('{http://regis-web.systemsbiology.net/protXML}protein'):	
		#go through each protein, which get abundance tags for each sample added
		abundance_per_sample = {}
		#count the peptide abundance for each sample
		for peptide in protein.findall('{http://regis-web.systemsbiology.net/protXML}peptide'):
			if args.TYP == 'unique' and peptide.attrib['is_nondegenerate_evidence'] == "N":
				continue
			sequence = peptide.attrib['peptide_sequence']
			for sample in peptides_samples.get(sequence):
				abundance_per_sample[sample] = abundance_per_sample.get(sample,0) + 1

		for sample in abundance_per_sample:
			#annotate back
			protein.append( ET.Element("parameter", name=sample, value=str(abundance_per_sample[sample]), type="abundance"))

	print "WRITING",args.OUT
	ET.ElementTree(root).write(args.OUT)

if __name__ == "__main__":
	main()
