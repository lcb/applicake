'''
Created on Jun 4, 2012

@author: quandtan
'''
import sys
from applicake.framework.logger import Logger
from applicake.utils.fileutils import FileUtils
from cStringIO import StringIO
from lxml import etree
from lxml.etree import SubElement

from unittest.case import TestCase
from applicake.utils.xmlutils import XmlUtils


class UnimodXmlParser():
    
    def __init__(self,path):
        self.ns = 'http://www.unimod.org/xmlns/schema/unimod_2'
        self.xml = etree.parse(path)
        self.xpath = etree.XPathEvaluator(self.xml,namespaces={'umod': self.ns})
        
    
    def get_dict(self):
        return XmlUtils.xml2d(self.xml.getroot())
    
    def get_elements(self):
        elems = self.xpath('.//umod:elements/umod:elem[@title][@mono_mass]')
        return dict((elem.get('title'), float(elem.get('mono_mass'))) for elem in elems)
    
    def get_modifications(self):
        mods = self.xpath('.//umod:modifications/umod:mod')
        dic = {}
        for mod in mods:            
            specificities = mod.findall('.//{%s}specificity' % self.ns)
            sites = []
            for specificity in specificities:
                sites.append(specificity.get('site'))            
            dic[mod.get('title')]={
                        'full_name': mod.get('full_name'),
                        'mono_mass': mod.find('.//{%s}delta' % self.ns).get('mono_mass'),
                        'avge_mass': mod.find('.//{%s}delta' % self.ns).get('avge_mass'),
                        'sites': sites
                        }
        return dic    
        
        
    

class UnimodDB(object):

    def __init__(self,log=None):
        if log is None:
            self.log = Logger.create(level='DEBUG',name='memory_logger',stream=sys.stderr)
        else:
            self.log = log

    def _parse_xml(self, path):        
        xml = etree.parse(path)
        
        
        
    def get_dict(self,path,format):
        if not FileUtils.is_valid_file(self.log,path):
            self.log.fatal('file [%s] is not valid.' % path)
            sys.exit(1)          
        formats = ['xml']          
        if format not in formats:
            self.log.fatal('format [%s] is none of the supported formats [%s].' % (format,formats))
            sys.exit(1)
        if format == formats[0]:
            self._parse_xml(path)  
                  

class UnimodXmlParserTest(TestCase):
    
    def setUp(self):
        self.path = '/Applications/OpenMS-1.9.0/share/OpenMS/CHEMISTRY/unimod.xml'
        self.log_stream = StringIO()
        self.log = Logger.create(level='DEBUG',name='memory_logger',stream=self.log_stream) 
        
    def test_get_elements(self):
        c = UnimodXmlParser(self.path)
        elems = c.xpath('.//umod:elements/umod:elem[@title][@mono_mass]')
        dic = dict((elem.get('title'), float(elem.get('mono_mass'))) for elem in elems)
        print dic
        
    def test_get_modifications(self):
        c = UnimodXmlParser(self.path)
        mods = c.get_modifications()
        print mods['Phospho']
           
    

#class UnimodDbTest(TestCase):
#
#    def setUp(self):
#        self.path = '/Applications/OpenMS-1.9.0/share/OpenMS/CHEMISTRY/unimod.xml'
#        self.log_stream = StringIO()
#        self.log = Logger.create(level='DEBUG',name='memory_logger',stream=self.log_stream)
#
#
#    def test_parse(self):
#        c = UnimodDb(self.log)
#        self.assertEqual(None,c.parse(self.path,format='xml'))
        



