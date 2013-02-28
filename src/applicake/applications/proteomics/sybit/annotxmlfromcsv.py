'''
Created on Jul 5, 2012

@author: lorenz
'''

import csv
import os
import re
from applicake.framework.interfaces import IApplication


class AnnotProtxmlFromUpdatedCsv(IApplication):
    
    def main(self,info,log):
        """
        After ProteinQuantifier puts abundances from consensusXML to csv,
        put abundances back to original protXML file.
        """
        #correct csv with right header
        mzxmls = info[self.MZXML]
        pepcsvprev = info['PEPCSV']
        info['PEPCSV'] = os.path.join(info[self.WORKDIR],'peptides.csv')
        self._correctcsv(pepcsvprev, info['PEPCSV'], mzxmls)
        protcsvprev = info['PROTCSV']
        info['PROTCSV'] = os.path.join(info[self.WORKDIR],'proteins.csv')
        self._correctcsv(protcsvprev,  info['PROTCSV'], mzxmls)
        
        #update protxml file using corrected csv files
        xml_in = info['PROTXML']
        xml_out = os.path.join(info[self.WORKDIR],os.path.basename(xml_in))
        prot_abundances = self._read_csv(info['PROTCSV'])
        self._annotate_protxml(xml_in,xml_out,prot_abundances,info['INDENT'])
        del info['INDENT']
        del info['DELIM']  
        info['PROTXML'] = xml_out 
        
        return 0,info
    
    def _correctcsv(self,infile,outfile,mzxmls):
        #descstring from ProteinQuantifier.c
        descstring = "# Files/samples associated with abundance values below: " 
        headerstring = '"abundance_'
        with open(infile) as source, open(outfile,'w') as target:
            for line in source:
                if descstring in line:
                    newline = descstring
                    for i,fle in enumerate(mzxmls,start=1):
                        newline += str(i) + ": '" + os.path.splitext(os.path.basename(fle))[0] + "', "
                    target.write(newline+'\n#\n')
                elif headerstring in line:
                    newline = line
                    for i,fle in enumerate(mzxmls,start=1):
                        newline = newline.replace("abundance_" + str(i), os.path.splitext(os.path.basename(fle))[0])
                    target.write(newline)
                else:
                    target.write(line)
                    
    def _read_csv(self,csv_in):
        #prot_abundances[PROTEINS][SAMPLE_ID] = abundance  
        prot_abundances = {}     
        with open(csv_in, "rb") as source:
            #the line containing the sampleids is the line before the data starts (with a '"')
            for line in source:
                if line.startswith('# Files/samples'):
                    sampleline = line
                if line.startswith('"'):
                    break
            sample_ids = re.compile("[0-9]+: '([^']+)'").findall(sampleline)
            n_samples = len(sample_ids)
            
            #the header is the first line starting with '"'. parse with csv.reader.next
            header = csv.reader([line]).next()
            for entry in csv.DictReader(source, header):
                abundances = {}
                for n in range(1,n_samples):
                    abundances[sample_ids[n]] = entry[sample_ids[n]]   
                proteins = entry['protein'].split("/")
                for protein in proteins:
                    prot_abundances[protein] = abundances                 
        return prot_abundances
            
    def _annotate_protxml(self,xml_in,xml_out,prot_abundances,indent):
        #this code is copied from hendriks annotate_protxml(protein_path, protxml_input, export_path)
        # annotate protXML file:
        with open(xml_in) as source:
            with open(xml_out, "w") as sink:
                for line in source:
                    if line.strip().startswith("<protein " ):
                        protein = self._get_attribute_value(line, "protein_name")
                        base_indent = line[:line.index("<")]
                        if len(indent) <= len(base_indent):
                            indent = base_indent + indent
                    elif line.strip() == ("</protein>"): # insert abundances here
                        abundances = prot_abundances.get(protein, {})
                        for file_id, abundance in abundances.items():
                            if abundance != "0":
                                sink.write('%s<parameter name="%s" value="%s" '
                                           'type="abundance"/>\n' % 
                                           (indent, file_id, abundance))
                    elif line.strip().startswith("<parameter"):
                        try:
                            if self._get_attribute_value(line, "type") == "abundance":
                                continue # throw away old abundance entries
                        except ValueError: # different "parameter" element
                            pass
                    sink.write(line)
                    
    def _get_attribute_value(self,line, attribute):
        """Get the value of an attribute from the XML element contained in 'line'"""
        pos0 = line.index(attribute + '="')
        pos1 = line.index('"', pos0) + 1
        pos2 = line.index('"', pos1)
        return line[pos1:pos2]   

    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, self.WORKDIR , 'Current WD')
        args_handler.add_app_args(log, self.MZXML , 'mzxmls')
        
        args_handler.add_app_args(log, 'PROTCSV' , 'Path to CSV input file containing prot abundances')
        args_handler.add_app_args(log, 'PEPCSV' , 'Path to CSV input file containing peptide abundances')
        args_handler.add_app_args(log, 'PROTXML' , 'Path to protXML input file')
        args_handler.add_app_args(log, 'DELIM', 'Field delimiter used in CSV input (optional)', default=',')
        args_handler.add_app_args(log, 'INDENT', 'Additional indentation for abundance entries in the protXML output (optional)', default='   ')
        return args_handler
