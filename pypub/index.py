#coding=utf-8
import web
from common import COMMON

class Index(object):
	"""docstring for Index"""
	def __init__(self):
		pass

	def GET(self):
		COMMON.check_login()
		render = COMMON.get_render()
		return render.index("曾奎")

	def POST(self):
		COMMON.check_login()
		return "POST Index";
		