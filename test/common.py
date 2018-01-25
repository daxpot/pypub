#coding=utf-8
import unittest
import sys
sys.path.append(".")
from pypub.common import COMMON

class commonTest(unittest.TestCase):
    def test_load_config(self):
        config = COMMON.load_config()
        print config['remote_root']
    def test_load_ssl(self):
    	COMMON.load_ssl(False)
    	config = {
			"certs": {			
				"key": "certs/test.key",
				"pem": "certs/test.pem"
			}
		}
    	COMMON.load_ssl(config)
    	config = {
			"certs": {			
				"key": "certs/test2.key",
				"pem": "certs/test2.pem"
			}
		}
    	COMMON.load_ssl(config)

if __name__ == '__main__':
    unittest.main()