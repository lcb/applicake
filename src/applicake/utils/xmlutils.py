"""
Created on Mar 31, 2012

@author: quandtan
"""

from xml.parsers import expat


class XmlValidator():
    """
    Validates xml files      
    """

    @staticmethod
    def _parsefile(path):
        parser = expat.ParserCreate()
        parser.ParseFile(open(path, "r"))
        return parser

    @staticmethod
    def is_wellformed(path):
        """
        Check if xml file is well-formed
        
        @type path: string 
        @param path: Path to the xml file that should be validated 
        
        @return: boolean
        """
        try:
            XmlValidator._parsefile(path)
            return True
        except Exception, e:
            print str(e)
            return False 
