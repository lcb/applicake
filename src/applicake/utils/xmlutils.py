'''
Created on Mar 31, 2012

@author: quandtan
'''

import xml.parsers.expat
from itertools import groupby
from lxml import etree



class XmlUtils():        
    
    @staticmethod
    def xml2d(e):
        """
        originated from: http://code.activestate.com/recipes/577722-xml-to-python-dictionary-and-back/
        
        Convert an etree into a dict structure
    
        @type  e: etree.Element
        @param e: the root of the tree
        @return: The dictionary representation of the XML tree
        """
        def _xml2d(e):
            kids = dict(e.attrib)
            for k, g in groupby(e, lambda x: x.tag):
                g = [ _xml2d(x) for x in g ] 
                kids[k]=  g
            return kids
        return { e.tag : _xml2d(e) }
    
    @staticmethod
    def d2xml(d):
        """
        originated from: http://code.activestate.com/recipes/577722-xml-to-python-dictionary-and-back/
        
        convert dict to xml
    
           1. The top level d must contain a single entry i.e. the root element
           2.  Keys of the dictionary become sublements or attributes
           3.  If a value is a simple string, then the key is an attribute
           4.  if a value is dict then, then key is a subelement
           5.  if a value is list, then key is a set of sublements
    
           a  = { 'module' : {'tag' : [ { 'name': 'a', 'value': 'b'},
                                        { 'name': 'c', 'value': 'd'},
                                     ],
                              'gobject' : { 'name': 'g', 'type':'xx' },
                              'uri' : 'test',
                           }
               }
        >>> d2xml(a)
        <module uri="test">
           <gobject type="xx" name="g"/>
           <tag name="a" value="b"/>
           <tag name="c" value="d"/>
        </module>
    
        @type  d: dict 
        @param d: A dictionary formatted as an XML document
        @return:  A etree Root element
        """
        def _d2xml(d, p):
            for k,v in d.items():
                if isinstance(v,dict):
                    node = etree.SubElement(p, k)
                    _d2xml(v, node)
                elif isinstance(v,list):
                    for item in v:
                        node = etree.SubElement(p, k)
                        _d2xml(item, node)
                else:
                    p.set(k, v)
    
        k,v = d.items()[0]
        node = etree.Element(k)
        _d2xml(v, node)
        return node    

class XmlValidator():  
    """
    Validates xml files      
    """  

    def _parsefile(self,path):
        parser = xml.parsers.expat.ParserCreate()
        parser.ParseFile(open(path, "r"))
        return parser

    def is_wellformed(self,path): 
        """
        Check if xml file is well-formed
        
        @type path: string 
        @param path: Path to the xml file that should be validated 
        
        @return: boolean
        """
        try:
            self._parsefile(path)
            return True
        except Exception, e:
            print str(e)
            return False 