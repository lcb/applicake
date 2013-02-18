'''
Created on Jul 5, 2012

@author: lorenz
'''

import csv
import os
import re
from applicake.framework.interfaces import IApplication


class AnnotProtxmlFromCsv(IApplication):
    
    def main(self,info,log):
        """
        After ProteinQuantifier puts abundances from consensusXML to csv,
        put abundances back to original protXML file.
        """
        xml_in = info['PROTXML']
        xml_out = os.path.join(info[self.WORKDIR],os.path.basename(xml_in))
        csv_in = info['PROTCSV']

        prot_abundances = self._read_csv(csv_in)
        self._annotate_protxml(xml_in,xml_out,prot_abundances)
        
        del info['PROTCSV']
        del info['INDENT']
        del info['DELIM']  
        info['PROTXML'] = xml_out 
        return 0,info
    
    def _read_csv(self,csv_in):
        #prot_abundances[PROTEINS][SAMPLE_ID] = abundance  
        prot_abundances = {}     
        with open(csv_in, "rb") as source:
            #the line containing the sampleids is the line before the data starts (with a '"')
            for line in source:
                if line.startswith('"'):
                    break
                sampleline = line
            sample_ids = re.compile("[0-9]+: '([^']+)'").findall(sampleline)
            n_samples = len(sample_ids)
            
            #the header is the first line starting with '"'. parse with csv.reader.next
            header = csv.reader([line]).next()
            for entry in csv.DictReader(source, header):
                abundances = {}
                for n in range(n_samples):
                    abundances[sample_ids[n]] = entry["abundance_%d" % n]   
                proteins = entry['protein'].split("/")
                for protein in proteins:
                    prot_abundances[protein] = abundances                 
        return prot_abundances
    
    def _annotate_protxml(self,xml_in,xml_out,prot_abundances):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(open(xml_in),"xml")
        for protein in soup('protein'):
            for abundance in protein(type='abundance'):
                prot = str(protein['protein_name'])
                id = str(abundance['name'])
                lfquant = prot_abundances.get(prot, {}).get(id,'0')
                if lfquant == '0':
                    abundance.extract()
                else:
                    abundance['value'] = lfquant
        
        with open(xml_out,'w') as f:
            f.write(soup.prettify())
            
#    def _annotate_protxml(self,xml_in,xml_out,prot_abundances,indent):
#        #this code is copied from hendriks annotate_protxml(protein_path, protxml_input, export_path)
#        # annotate protXML file:
#        with open(xml_in) as source:
#            with open(xml_out, "w") as sink:
#                for line in source:
#                    if line.strip().startswith("<protein " ):
#                        protein = self._get_attribute_value(line, "protein_name")
#                        base_indent = line[:line.index("<")]
#                        if len(indent) <= len(base_indent):
#                            indent = base_indent + indent
#                    elif line.strip() == ("</protein>"): # insert abundances here
#                        abundances = prot_abundances.get(protein, {})
#                        for file_id, abundance in abundances.items():
#                            if abundance != "0":
#                                sink.write('%s<parameter name="%s" value="%s" '
#                                           'type="abundance"/>\n' % 
#                                           (indent, file_id, abundance))
#                    elif line.strip().startswith("<parameter"):
#                        try:
#                            if self._get_attribute_value(line, "type") == "abundance":
#                                continue # throw away old abundance entries
#                        except ValueError: # different "parameter" element
#                            pass
#                    sink.write(line)
#                    
#    def _get_attribute_value(self,line, attribute):
#        """Get the value of an attribute from the XML element contained in 'line'"""
#        pos0 = line.index(attribute + '="')
#        pos1 = line.index('"', pos0) + 1
#        pos2 = line.index('"', pos1)
#        return line[pos1:pos2]   

    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, self.WORKDIR , 'Current WD')
        args_handler.add_app_args(log, 'CSV' , 'Path to CSV input file containing abundances')
        args_handler.add_app_args(log, 'PROTXML' , 'Path to protXML input file')
        args_handler.add_app_args(log, 'DELIM', 'Field delimiter used in CSV input (optional)', default=',')
        args_handler.add_app_args(log, 'INDENT', 'Additional indentation for abundance entries in the protXML output (optional)', default='   ')
        
        return args_handler
