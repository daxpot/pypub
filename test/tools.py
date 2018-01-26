#coding=utf-8
import unittest
import sys
sys.path.append(".")
from pypub.tools import CONFIG_T, COMMON

class commonTest(unittest.TestCase):
    def test_load_config(self):
        print "test_load_config"
        config = CONFIG_T.load_config()
        print config['remote_root']
    def test_load_ssl(self):
        print "test_load_ssl"
    	CONFIG_T.load_ssl()
    	config = {
			"certs": {			
				"key": "certs/test.key",
				"pem": "certs/test.pem"
			}
		}
    	CONFIG_T.load_ssl()
    	config = {
			"certs": {			
				"key": "certs/test2.key",
				"pem": "certs/test2.pem"
			}
		}
    	CONFIG_T.load_ssl()
    def test_get_apps(self):
        print "test_get_apps"
    	apps = CONFIG_T.get_apps()
    	print apps

    def test_db(self):
        print "test_db"
        db = COMMON.get_db()
        print db.Put("test", "test_value")
        print db.Get("test")
    def test_db2(self):
        print "test_db2"
        db = COMMON.get_db()
        print db.Get("test")
        print db.GetStats("test234234")
        print list(db.RangeIter(key_from='test', key_to='test'))


if __name__ == '__main__':
    unittest.main()