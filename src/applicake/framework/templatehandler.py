"""
Created on Apr 23, 2012

@author: quandtan
"""

from string import Template

from applicake.framework.keys import Keys

from applicake.framework.interfaces import ITemplateHandler


class BasicTemplateHandler(ITemplateHandler):
    """
    Basic implementation of the ITemplateHandler interface.
    """

    def read_template(self, info, log):
        if not info.has_key(Keys.TEMPLATE):
            raise Exception("Cannot read template: TEMPLATE key in info not found")

        fh = open(info[Keys.TEMPLATE], 'r+')
        template = fh.read()
        return template, info

    def modify_template(self, info, log, template=None):
        """
        replaces $VARS in template if found in info, otherwise leaves $VARS. 
        NOTE: The first non-identifier character after the $ character terminates this 
        placeholder specification. Valid Python identifiers: A-Z a-z 0-9 _
        """
        if template is None:
            log.debug("Template empty, performing read()")
            template, info = self.read_template(info, log)

        mod_template = Template(template).safe_substitute(info)

        if Keys.TEMPLATE in info:
            log.debug("Found TEMPLATE key, performing write()")
            self.write_template(info, log, mod_template)
        return mod_template, info

    def write_template(self, info, log, template):
        if not info.has_key(Keys.TEMPLATE):
            raise Exception("Cannot write template: TEMPLATE key in info not found")

        fh = open(info[Keys.TEMPLATE], 'w+')
        fh.write(template)
        fh.close()
        return info
    
