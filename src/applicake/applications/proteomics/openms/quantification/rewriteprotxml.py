'''
Created on 18 Feb 2013

@author: lorenz
'''

import csv,re,os
from applicake.framework.interfaces import IApplication

class RewriteAbundancesToProtXML(IApplication):
    
    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, 'PROTCSV', '')
        args_handler.add_app_args(log, 'PROTXML', '')
        args_handler.add_app_args(log, 'WORKDIR', '')
        return args_handler
    
    def main(self,info,log):
        csv_in = info['PROTCSV']
        protxml_in = info['PROTXML']
        protxml_out = os.path.join(info['WORKDIR'],'abundance.prot.xml')
        self._annotate_protxml(csv_in,protxml_in,protxml_out)
        return 0,info
        
    def _annotate_protxml(self,csv_in, protxml_in, protxml_out, delim=",", indent="   "):
        """Annotate a protXML file with protein abundance data.
    
        Required arguments:
        'csv_in' - Path to CSV input file.
        'protXML_in' - Path to protXML input file.
        'protXML_out' - Path to protXML output file.
        'delim' - Field delimiter used in CSV input.
        'indent' - Additional indentation for abundance entries in the protXML 
        output.
        """
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
                self._add_entry(entry, n_samples, result)
    
        # get file IDs associated with abundance values:
        regexp = re.compile("[0-9]+: '([^']+)'")
        matches = regexp.findall(comments[-1])
        file_ids = [os.path.basename(match).split(".")[0] for match in matches]
    
        # annotate protXML file:
        with open(protxml_in) as source:
            with open(protxml_out, "w") as sink:
                for line in source:
                    if line.strip().startswith("<protein "):
                        protein = self._get_attribute_value(line, "protein_name")
                        base_indent = line[:line.index("<")]
                        if len(indent) <= len(base_indent):
                            indent = base_indent + indent
                    elif line.strip() == ("</protein>"): # insert abundances here
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
    
    def _add_entry(self,entry, n_samples, result):
        """Process a line from the CSV input file"""
        abundances = [entry["abundance_" + str(n)] for n in range(n_samples)]
        proteins = entry["protein"].split("/")
        for protein in proteins:
            result[protein] = abundances
            
    def _get_attribute_value(self,line, attribute):
        """Get the value of an attribute from the XML element contained in 'line'"""
        pos0 = line.index(attribute + '="')
        pos1 = line.index('"', pos0) + 1
        pos2 = line.index('"', pos1)
        return line[pos1:pos2]