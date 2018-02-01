#coding=utf-8
import unittest
import sys
sys.path.append(".")
from pypub import PubCore

class pubcoreTest(unittest.TestCase):
    def test_publish(self):
        app = {
            "name": "app1",
            "dir": "./testapp/app1"
        }
        pc = PubCore(app)
        print pc.publish("0.0.1")

if __name__ == '__main__':
    unittest.main()