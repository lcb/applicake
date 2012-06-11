'''
Created on Jun 10, 2012

@author: quandtan
'''

from applicake.applications.proteomics.base import MzMlModifier
from applicake.framework.templatehandler import BasicTemplateHandler

class PeakPickerHighRes(MzMlModifier):
    """
    Wrapper for the OpenMS tools ....
    """

    def __init__(self):
        """
        Constructor
        """
        # http://thingspython.wordpress.com/2010/09/27/another-super-wrinkle-raising-typeerror/
        self._as_super = super(PeakPickerHighRes,self)
        self._as_super.__init__()
        self._default_prefix = 'PeakPickerHiRes' # default prefix, usually the name of the OpenMS-tool


    def get_template_handler(self):
        """
        See interface
        """
        return PeakPickerHighResTemplate()


    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(PeakPickerHighRes, self).set_args(log,args_handler)
        args_handler.add_app_args(log, 'SIGNAL_TO_NOISE', 'Signal to noise ')
        return args_handler


class PeakPickerHighResTemplate(BasicTemplateHandler):
    """
    Template handler for PeakPickerHighRes.
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """<?xml version="1.0" encoding="ISO-8859-1"?>
<PARAMETERS version="1.3" xsi:noNamespaceSchemaLocation="http://open-ms.sourceforge.net/schemas/Param_1_3.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NODE name="PeakPickerHiRes" description="Finds mass spectrometric peaks in profile mass spectra.">
    <ITEM name="version" value="1.9.0" type="string" description="Version of the tool that generated this parameters file." tags="advanced" />
    <NODE name="1" description="Instance &apos;1&apos; section for &apos;PeakPickerHiRes&apos;">
      <ITEM name="in" value="$ORGMZML" type="string" description="input profile data file " tags="input file,required" restrictions="*.mzML" />
      <ITEM name="out" value="$MZML" type="string" description="output peak file " tags="output file,required" restrictions="*.mzML" />
      <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
      <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
      <ITEM name="threads" value="$THREADS" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
      <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
      <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
      <NODE name="algorithm" description="Algorithm parameters section">
        <ITEM name="signal_to_noise" value="$SIGNAL_TO_NOISE" type="float" description="Minimal signal-to-noise ratio for a peak to be picked (0.0 disables SNT estimation!)" restrictions="0:" />
        <ITEM name="ms1_only" value="false" type="string" description="If true, peak picking is only applied to MS1 scans. Other scans are copied to the output without changes." restrictions="true,false" />
      </NODE>
    </NODE>
  </NODE>
</PARAMETERS>

"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info