#coding=utf-8
import web
import json
from tools import WEB_T, CONFIG_T, COMMON, PutT

class Detail(object):
    """docstring for Detail"""
    def __init__(self):
        pass

    def render(self, infos, errmsg):
    	render = WEB_T.get_render()
    	session = WEB_T.get_session()
    	return render.detail(session.username, infos, errmsg)

    def get_infos(self):
    	i = web.input()
    	appid = i.get('appid')
    	db = COMMON.get_db()
    	appver = COMMON.dbget("cur-%s" % appid, None, "json")
    	if not appver:
    		return [], "appid错误"
    	page = i.get("page")
    	if not page:
    		page = 1
    	appver.setdefault("history", [])
    	infos = {"vers": {}, "history": appver["history"]}
    	for ver in appver["history"]:
    		key = "ver-%s-%s" % (appid, ver)
    		infos["vers"][ver] = COMMON.dbget(key, None, "json")
    	return infos, ""

    def GET(self):
        WEB_T.check_login()
    	infos, errmsg = self.get_infos();
    	print infos
    	return self.render(infos, errmsg)