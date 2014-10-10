#!/usr/bin/env python
#reimplementation of the tpp2viewer tool from lucia

import sys
import subprocess
import os
import stat

getexperiment = "/IMSB/scripts/dss_client/bin/getexperiment"
getmsdata = "/IMSB/scripts/dss_client/bin/getmsdata"
if not os.path.exists(getexperiment):
    getexperiment = "getexperiment"
    getmsdata = "getmsdata"


def main():
    if len(sys.argv) < 2 or '-h' in sys.argv[1]:
        print """Usage: %s EXPERIMENT_CODE [full]
Gets TPP search result EXPERIMENT_CODE from openbis and makes petunia compatible pep/prot.xml.
If [full] is set the corresponding mzXMLs are downloaded (can use lots of time and diskspace!)
Caveats: 
- To see MS2 spectra in Lorikeet the [full] option is required
- The pepxml viewer can somtimes not display low-scoring proteins""" % os.path.basename(
            __file__)
        return 1


    exp = sys.argv[1]
    base = os.path.join(os.environ["PWD"], 'tpp2viewer3_' + exp)
    check_folder_permissions(os.environ["PWD"])
    get_experiment(exp)
    pepxml, protxml = get_xmlpaths(exp)
    extractfasta = extract_fasta(protxml, base)
    fixpepxml = fix_pepxml(pepxml, base, extractfasta)
    fixprotxml = fix_protxml(protxml, base, extractfasta, fixpepxml)

    #mzXML only on request
    if len(sys.argv) == 3 and 'full' in sys.argv[2]:
        get_datasets(fixpepxml)

    print_link(base, fixpepxml, fixprotxml)
    return 0

def check_folder_permissions(path):
    mode = os.stat(path).st_mode
    if not bool(mode & stat.S_IWOTH):
        try:
            os.chmod(path, mode | stat.S_IWOTH)
        except:
            raise Exception("Petunia will create temporary files in folder %s, thus it must be writable by 'everybody'. "
                            "Please change that!" % path)


def get_experiment(exp):
    if os.path.exists(exp):
        print "Found folder %s, skipping download" % exp
    else:
        print "Downloading experiment " + exp
        p = subprocess.Popen(getexperiment + " -v -r /dev/null " + exp, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, _ = p.communicate()
        if p.returncode != 0:
            raise Exception("getexperiment failed")

        for line in stdout.split('\n'):
            if "DataSet" in line:
                folder = line.split('[')[1].split(',')[0]
        subprocess.check_call("mv %s %s" % (folder, exp), shell=True)


def get_xmlpaths(exp):
    ap = os.path.abspath(exp)
    pepxml = None
    protxml = None
    for file in os.listdir(exp):
        if '.pep.xml' in file:
            pepxml = os.path.join(ap, file)
        if '.prot.xml' in file:
            protxml = os.path.join(ap, file)
    if not pepxml:
        print "no protxml in experiment folder found"
        return 1
    if not protxml:
        print "no protxml in experiment folder found"
        return 1
    return pepxml, protxml


def extract_fasta(xml_in, base):
    print "Extracting fasta"
    fastapath = base + '.fasta'
    fasta = open(fastapath, 'w')
    for line in open(xml_in, 'r'):
        if "protein_description" in line:
            tagcontent = get_attribute_value(line, "protein_description")
            name, seq = tagcontent.split("\SEQ=")
            fasta.write(">" + name + "\n")
            fasta.write(seq + "\n")
    fasta.close()
    return fastapath


def fix_pepxml(pepxml, base, fastapath):
    print "Fixing pepxml"
    dirname = os.path.dirname(base)
    fixpepxml = base + '.pep.xml'
    sink = open(fixpepxml, 'w')
    for line in open(pepxml, 'r'):
        if '<msms_pipeline_analysis ' in line:
            line = set_attribute_value(line, 'summary_xml', fixpepxml)
        if '<search_database ' in line:
            line = set_attribute_value(line, 'local_path', fastapath)
        if '<msms_run_summary' in line:
            mzxml = os.path.basename(get_attribute_value(line, 'base_name'))
            fullmzpath = os.path.join(dirname, mzxml)
            line = set_attribute_value(line, 'base_name', fullmzpath)
        sink.write(line)
    sink.close()
    return fixpepxml


def get_attribute_value(line, attribute):
    pos0 = line.index(attribute + '="')
    pos1 = line.index('"', pos0) + 1
    pos2 = line.index('"', pos1)
    return line[pos1:pos2]


def set_attribute_value(line, attribute, newvalue):
    pos0 = line.index(attribute + '="')
    pos1 = line.index('"', pos0) + 1
    pos2 = line.index('"', pos1)
    return line[:pos1] + newvalue + line[pos2:]


def fix_protxml(protxml, base, fastapath, pepxmlpath):
    print "Fixing protxml"
    fixprotxml = base + '.prot.xml'
    sink = open(fixprotxml, 'w')
    for line in open(protxml, 'r'):
        if '<protein_summary ' in line:
            line = set_attribute_value(line, 'summary_xml', fastapath)
        if '<protein_summary_header ' in line:
            line = set_attribute_value(line, 'reference_database', fastapath)
            line = set_attribute_value(line,'source_files', pepxmlpath)       
            line = set_attribute_value(line,'source_files_alt', pepxmlpath)  
        sink.write(line)
    sink.close()
    #fix_industinguishable_peptides(fixprotxml, fixprotxml)
    return fixprotxml


def fix_industinguishable_peptides(xml_in, xml_out):
    #required, otherwise tpp2 does not show all proteins in prot.xml viewer
    xml_out_lines = []
    last_peptide_line = ""

    for line in open(xml_in, 'r'):
        if "peptide " in line and "nsp_adjusted_probability" in line:
            if not "calc_neutral_pep_mass" in line:
                last_peptide_line = line
            else:
                last_peptide_line = ""
                xml_out_lines += line
        else:
            if "</peptide>" in line:
                if not last_peptide_line:
                    xml_out_lines += line
            else:
                if "indistinguishable_peptide" in line:
                    if not last_peptide_line:
                        print "WARNING: can't replace indistinguishable peptide: " + line
                        xml_out_lines += line
                else:
                    xml_out_lines += line
    if len(xml_out) == 0:
        xml_out = xml_in
    with open(xml_out, 'w') as sink:
        for line in xml_out_lines:
            sink.write(line)


def get_datasets(fixpepxml):
    codes_names = {}
    for line in open(fixpepxml, 'r'):
        if '<spectrum_query' in line:
            pos0 = line.index('spectrum="') + 1
            pos1 = line.index('"', pos0) + 1
            pos2 = line.index('~', pos1) + 1
            pos3 = line.index('.', pos1)
            filename = line[pos1:pos3] + ".mzXML"
            code = line[pos2:pos3]
            codes_names[code] = filename

    for code, filename in codes_names.items():
        if os.path.exists(filename):
            print "Found file %s, skipping download" % filename
        else:
            print "Downloading mzXML " + filename
            p = subprocess.Popen("%s -v -r /dev/null %s" % (getmsdata, code), shell=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout, _ = p.communicate()
            if p.returncode != 0:
                raise Exception("getdataset failed")

            for line in stdout.split('\n'):
                if "downloaded dataset file" in line:
                    mzxml = line.split(' ')[-1]
            subprocess.check_call("ln -s %s %s" % (mzxml, filename), shell=True)


def print_link(base, fixpepxml, fixprotxml):
    print """To view results use:
https://imsb-ra-tpp.ethz.ch/tpp/cgi-bin/PepXMLViewer.cgi?xmlFileName=%s
https://imsb-ra-tpp.ethz.ch/tpp/cgi-bin/protxml2html.pl?xmlfile=%s
NEW BETA:
https://imsb-ra-tpp.ethz.ch/tpp/cgi-bin/ProtXMLViewer.pl?file=%s""" % ( fixpepxml, fixprotxml, fixprotxml)
    #petunia uses html/ as user folder!
    if not 'html/' in base:
        print "WARNING: These links might not work if the files are not in the html/ folder!"


if __name__ == "__main__":
    sys.exit(main())
