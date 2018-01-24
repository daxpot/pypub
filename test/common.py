#coding=utf-8
import unittest
import sys
sys.path.append(".")
from tools import common

class commonTest(unittest.TestCase):
    def test_load_config(self):
        ret = common.TOOLS_COMMON.load_config()
        print ret['remote_root']

if __name__ == '__main__':
    unittest.main()