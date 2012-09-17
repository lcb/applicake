'''
Created on Jul 5, 2012

@author: lorenz
'''

import csv
import os
import re
from applicake.framework.interfaces import IApplication


class AnnotXmlFromCsv(IApplication):
    
    def main(self,info,log):
        """
        After ProteinQuantifier puts abundances from consensusXML to csv,
        put abundances back to original protXML file.
        """
        #annotate_protxml(protein_path, protxml_input, export_path)
        if info['PROTXML']:
            pti = 'protein'
            xml_in = info['PROTXML']
        else: 
            pti = 'peptide'
            xml_in = info['PEPXML']
        xml_out = os.path.join(self.WORKDIR,os.path.basename(xml_in))
        csv_in = info['CSV']
        indent = info['INDENT']
        
        result = {}
        with open(csv_in, "rb") as source:
            comments = []
            line = source.readline().strip()
            while line and line.startswith("#"): # comment line
                comments.append(line)
                line = source.readline().strip()
            header = csv.reader([line]).next()
            n_samples = sum([item.startswith("abundance_") for item in header])
            # read data:
            for entry in csv.DictReader(source, header):
                abundances = [entry["abundance_" + str(n)] for n in range(n_samples)]
                proteins = entry[pti].split("/")
                for protein in proteins:
                    result[protein] = abundances
    
        # get file IDs associated with abundance values:
        regexp = re.compile("[0-9]+: '([^']+)'")
        matches = regexp.findall(comments[-1])
        file_ids = [os.path.basename(match).split(".")[0] for match in matches]
    
        # annotate protXML file:
        with open(xml_in) as source:
            with open(xml_out, "w") as sink:
                for line in source:
                    if line.strip().startswith("<%s "%pti ):
                        protein = self._get_attribute_value(line, "%s_name"%pti)
                        base_indent = line[:line.index("<")]
                        if len(indent) <= len(base_indent):
                            indent = base_indent + indent
                    elif line.strip() == ("</%s>"%pti): # insert abundances here
                        abundances = result.get(protein, [])
                        for file_id, abundance in zip(file_ids, abundances):
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
        
        del info['CSV']
        del info['INDENT']
        del info['DELIM']  
        if info['PROTXML']:
            info['PROTXML'] = xml_out 
        else: 
            info['PEPXML'] = xml_out
                      
        return 0,info
    
    def _get_attribute_value(self,line, attribute):
        """Get the value of an attribute from the XML element contained in 'line'"""
        pos0 = line.index(attribute + '="')
        pos1 = line.index('"', pos0) + 1
        pos2 = line.index('"', pos1)
        return line[pos1:pos2]   

    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, 'CSV' , 'Path to CSV input file containing abundances')
        args_handler.add_app_args(log, 'PEPXML' , 'Path to pepXML input file', default=None)
        args_handler.add_app_args(log, 'PROTXML' , 'Path to protXML input file', default=None)
        args_handler.add_app_args(log, 'DELIM', 'Field delimiter used in CSV input', default=',')
        args_handler.add_app_args(log, 'INDENT', 'Additional indentation for abundance entries in the protXML output', default='   ')
        
        return args_handler

    