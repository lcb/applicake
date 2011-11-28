'''
Created on Nov 28, 2011

@author: quandtan
'''

from distutils.core import setup

setup(
    name='applicake',
    version='0.0.7',
    description='A framework that simplifies the wrapping of external tools by standardizing input parameters, logging messages and output streams.',
    homepage='http://code.google.com/p/applicake',
    author='Andreas Quandt',
    author_email='applicake.pypi@gmail.com',
    packages=['applicake',],
    license='Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY-NC-SA 3.0)',
    long_description=open('README.txt').read(),
    url='http://code.google.com/p/applicake',
    #platforms=['Python 2.6',]
)   
