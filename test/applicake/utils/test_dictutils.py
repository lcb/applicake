'''
Created on Apr 2, 2012

@author: quandtan
'''
import unittest
from StringIO import StringIO

from applicake.utils.dictutils import DictUtils
from applicake.framework.logger import Logger


class Test(unittest.TestCase):
    def setUp(self):
        log_stream = StringIO()
        self.log = Logger.create(level='DEBUG', name='memory_logger', stream=log_stream)
        self.d1 = {
            'BASEDIR': '/tmp',
            'COMMENT': 'hello world',
            'FILE_IDX': 0,
            'JOB_IDX': 0,
            'LOG_LEVEL': 'INFO',
            'OUTPUT': '../../../data/output.ini',
            'PARAM_IDX': 0,
            'STORAGE': 'memory',
            'SECTION': {'SUB_1': 11},
            'LIST': [11]
        }
        self.d2 = {
            'BASEDIR': '/tmp',
            'COMMENT': 'hello world',
            'FILE_IDX': 0,
            'JOB_IDX': 0,
            'LOG_LEVEL': 'INFO',
            'OUTPUT': '../../../data/output.ini',
            'PARAM_IDX': 0,
            'STORAGE': 'memory',
            'SECTION': {'SUB_2': 22},
            'LIST': [22, 222]
        }


    def tearDown(self):
        del self.d1
        del self.d2


    def test_extract(self):
        res = DictUtils.extract(self.d1, ['FILE_IDX'], include=True)
        expected = {
            'FILE_IDX': 0
        }
        self.assertDictEqual(res, expected, '')
        res = DictUtils.extract(self.d1, ['FILE_IDX'], include=False)
        expected = {
            'BASEDIR': '/tmp',
            'COMMENT': 'hello world',
            'JOB_IDX': 0,
            'LOG_LEVEL': 'INFO',
            'OUTPUT': '../../../data/output.ini',
            'PARAM_IDX': 0,
            'STORAGE': 'memory',
            'SECTION': {'SUB_1': 11},
            'LIST': [11]
        }
        self.assertDictEqual(res, expected, '')

    def test_merge(self):
        res = DictUtils.merge(self.log, self.d1, self.d2, priority='left')
        assert res == {
            'BASEDIR': '/tmp',
            'COMMENT': 'hello world',
            'FILE_IDX': 0,
            'JOB_IDX': 0,
            'LOG_LEVEL': 'INFO',
            'OUTPUT': '../../../data/output.ini',
            'PARAM_IDX': 0,
            'STORAGE': 'memory',
            'SECTION': {'SUB_1': 11},
            'LIST': [11]
        }
        res = DictUtils.merge(self.log, self.d1, self.d2, priority='right')
        assert res == {
            'BASEDIR': '/tmp',
            'COMMENT': 'hello world',
            'FILE_IDX': 0,
            'JOB_IDX': 0,
            'LOG_LEVEL': 'INFO',
            'OUTPUT': '../../../data/output.ini',
            'PARAM_IDX': 0,
            'STORAGE': 'memory',
            'SECTION': {'SUB_2': 22},
            'LIST': [22, 222]
        }
        res = DictUtils.merge(self.log, self.d1, self.d2, priority='flatten_sequence')
        assert res == {
            'BASEDIR': '/tmp',
            'COMMENT': 'hello world',
            'FILE_IDX': 0,
            'JOB_IDX': 0,
            'LOG_LEVEL': 'INFO',
            'OUTPUT': '../../../data/output.ini',
            'PARAM_IDX': 0,
            'STORAGE': 'memory',
            'SECTION': ['SUB_1', 'SUB_2'],
            'LIST': [11, 22, 222]
        }


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_Merge']
    unittest.main()
