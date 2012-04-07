'''
Created on Mar 31, 2012

@author: quandtan
'''

import xml.parsers.expat

class XmlValidator():  
    """
    Validates xml files      
    """  

    def _parsefile(self,path):
        parser = xml.parsers.expat.ParserCreate()
        parser.ParseFile(open(path, "r"))
        return parser

    @staticmethod
    def is_wellformed(self,path): 
        """
        Check if xml file is well-formed
        """
        try:
            self._parsefile(path)
            return True
        except Exception, e:
            print str(e)
            return False 