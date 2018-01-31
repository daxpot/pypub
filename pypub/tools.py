#coding=utf-8
import sys
import commentjson
import os
import logging
import time
from web.wsgiserver import CherryPyWSGIServer
import web
import hashlib
import leveldb
import json

class ConfigT(object):
	def __init__(self):
		pass

	def load_config(self):
		config_path = "config.json"
		argv = COMMON.get_command_arg("-c")
		if argv:
			config_path = argv
		try:
			with open(config_path, "r") as f:
				return commentjson.loads(f.read())
		except Exception, e:
			logging.error(e)
		return False

	def load_ssl(self):
		config = self.load_config()
		if config and "certs" in config and "key" in config["certs"] and "pem" in config["certs"]:
			CherryPyWSGIServer.ssl_certificate = config["certs"]["pem"]
			CherryPyWSGIServer.ssl_private_key = config["certs"]["key"]

	def init_logger(self, logLevel=logging.INFO):
	    log_root = 'data/log'
	    if not os.path.exists(log_root):
	        os.makedirs(log_root)
	    cur_time = time.strftime("%Y%m%d", time.localtime())

	    log_file_name = '%s/%s.log' %(log_root, cur_time)
	    logging.basicConfig(level=logLevel,
	                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
	                datefmt='%a, %d %b %Y %H:%M:%S',
	                filename=log_file_name,
	                filemode='a+')

	    console = logging.StreamHandler()
	    console.setLevel(logging.DEBUG)
	    formatter = logging.Formatter('%(asctime)s\t[%(levelname)s]\t%(message)s')
	    console.setFormatter(formatter)
	    logging.getLogger('').addHandler(console)

	def get_apps(self, appid=None):
		config = self.load_config()
		apps = []
		app_paths = {}
		if "apps" in config:
			apps = config["apps"]
			for app in apps:
				if "dir" in app:
					if "name" not in app:
						app["name"] = os.path.basename(app["dir"])
					if "remote_dir" in app:
						app["remote_dir"] = app["remote_dir"].rstrip("/")
					app["dir"] = app["dir"].rstrip("/")
					app_paths[os.path.abspath(app["dir"])] = 1
				else:
					apps.remove(app)
		dirs = []
		if "apps_root" in config:
			apps_root = config["apps_root"].rstrip("/")
			files = os.listdir(apps_root)
			for f in files:
				path = "%s/%s" % (apps_root, f)
				abspath = os.path.abspath(path)
				if os.path.isdir(path) and abspath not in app_paths:
					apps.append({
						"name": f,
						"dir": path
					})
					app_paths[abspath] = 1
		if appid:
			app = None
			for item in apps:
				if item["name"] == appid:
					return item
			return None
		return apps

	def get_servers(self, host=None):
		config = self.load_config()
		servers = []
		remote_root = ""
		if "remote_root" in config:
			remote_root = config["remote_root"]
		if "servers" in config and isinstance(config["servers"], list):
			for server in config["servers"]:
				if "host" in server and isinstance(server["host"], unicode) and server["host"] and "user" in server and isinstance(server["user"], unicode) and server["user"] and "password" in server and isinstance(server["password"], unicode) and server["password"]:
					if "remote_root" not in server:
						server["remote_root"] = remote_root
					if not isinstance(server["remote_root"], unicode):
						server["remote_root"] = ""
					if "port" not in server or not isinstance(server["port"], int):
						server["port"] = 22
					server["remote_root"] = server["remote_root"].rstrip("/")
					servers.append(server)
		if host:
			server = None
			for item in servers:
				if item["host"] == host:
					return item
			return None
		return servers



class WebT(object):
	def __init__(self):
		self.session = None
		self.web_render = web.template.render("templates", base="layout")

	def get_render(self):
		return self.web_render

	def check_login(self):
		session = self.get_session()
		if session.get("logged_in", False):
			return True
		else:
			raise web.seeother('/login')
			return False
	def get_session(self, app=None):
		if self.session:
			return self.session
		elif app:
			self.session = web.session.Session(app, web.session.DiskStore('data/sessions'))
			return self.session
		else:
			logging.error("获取session错误")
			return None

class Common(object):
	"""docstring for Common"""
	def __init__(self):
		print "Common init"
		self.leveldb = None

	def get_command_arg(self, param):
		arg_len = len(sys.argv)
		for i in range(0, arg_len):
			if sys.argv[i] == param and (i+1)<arg_len:
				return sys.argv[i+1]
		return False


	def get_md5(self, s):
		return hashlib.md5(s).hexdigest()

	def get_file_md5(self, file):
		with open(file, "r") as f:
			return self.get_md5(f.read())

	def get_db(self):
		if not self.leveldb:
			self.leveldb = leveldb.LevelDB("data/leveldb", create_if_missing=True)
		return self.leveldb

	def dbget(self, key, default=None, format="string"):
		db = self.get_db()
		try:
			data = db.Get(key)
			if format == "json":
				data = json.loads(data)
			return data
		except KeyError:
			return default
	def dbput(self, key, value, format='string'):
		db = self.get_db()
		if format == "json":
			value = json.dumps(value)
		db.Put(key, value)


COMMON = Common()
WEB_T = WebT()
CONFIG_T = ConfigT()
