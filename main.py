#coding=utf-8
import web
from web.wsgiserver import CherryPyWSGIServer
from tools import common

CherryPyWSGIServer.ssl_certificate = "certs/test.pem"
CherryPyWSGIServer.ssl_private_key = "certs/test.key"

class index(object):
	"""docstring for index"""
	def __init__(self):
		pass

	def GET(self):
		return "Hello Index";

def main():
	urls = ("/.*", "index")
	app = web.application(urls, globals())
	app.run()

if __name__ == '__main__':
	main()