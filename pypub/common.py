#coding=utf-8
import sys
import commentjson
import os
import logging
import time
from web.wsgiserver import CherryPyWSGIServer
import web
import hashlib

class Common(object):
	"""docstring for Common"""
	def __init__(self):
		print "Common init"
		self.session = None
		self.web_render = web.template.render("templates", base="layout")

	def get_session(self, app=None):
		if self.session:
			return self.session
		elif app:
			self.session = web.session.Session(app, web.session.DiskStore('sessions'))
			return self.session
		else:
			logging.error("获取session错误")
			return None

	def check_login(self):
		session = self.get_session()
		if session.get("logged_in", False):
			return True
		else:
			raise web.seeother('/login')
			return False

	def init_logger(self, logLevel):
	    log_root = 'log'
	    if not os.path.exists(log_root):
	        os.makedirs(log_root)
	    cur_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())

	    log_file_name = '%s/%s.log' %(log_root, cur_time)
	    logging.basicConfig(level=logLevel,
	                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
	                datefmt='%a, %d %b %Y %H:%M:%S',
	                filename=log_file_name,
	                filemode='w')

	    console = logging.StreamHandler()
	    console.setLevel(logging.DEBUG)
	    formatter = logging.Formatter('%(asctime)s\t[%(levelname)s]\t%(message)s')
	    console.setFormatter(formatter)
	    logging.getLogger('').addHandler(console)

	def load_ssl(self, config):
		if config and "certs" in config and "key" in config["certs"] and "pem" in config["certs"]:
			CherryPyWSGIServer.ssl_certificate = config["certs"]["pem"]
			CherryPyWSGIServer.ssl_private_key = config["certs"]["key"]

	def get_command_arg(self, param):
		arg_len = len(sys.argv)
		for i in range(0, arg_len):
			if sys.argv[i] == param and (i+1)<arg_len:
				return sys.argv[i+1]
		return False


	def load_config(self):
		config_path = "config.json"
		argv = self.get_command_arg("-c")
		if argv:
			config_path = argv
		try:
			with open(config_path, "r") as f:
				return commentjson.loads(f.read())
		except Exception, e:
			logging.error(e)
		return False

	def get_render(self):
		return self.web_render

	def get_md5(self, s):
		return hashlib.md5(s).hexdigest()

	def get_file_md5(self, file):
		with open(file, "r") as f:
			return self.get_md5(f.read())


COMMON = Common()
