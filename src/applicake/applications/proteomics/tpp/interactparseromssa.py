'''
Created on Jun 25, 2012

@author: loblum
'''

from applicake.applications.proteomics.tpp.interactparser import InteractParser
from applicake.framework.templatehandler import BasicTemplateHandler

class InteractParserOMSSA(InteractParser):
    def get_template_handler(self):
        return InteractParserOMSSATemplate()
    
class InteractParserOMSSATemplate(BasicTemplateHandler):
    def read_template(self, info, log):    
        template = """-L7 -E$ENZYME -C -P 
"""
        return template,info