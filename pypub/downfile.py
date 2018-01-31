#coding=utf-8
import web
import os
from tools import WEB_T, CONFIG_T, COMMON

class Downfile(object):
    """docstring for Downfile"""
    def __init__(self):
        pass

    def GET(self):
        WEB_T.check_login()
        i = web.input()

        appid = i.get('appid')
        file = i.get('src')
        ver = i.get('ver')
        app = CONFIG_T.get_apps(appid)
        if not app:
            raise web.notfound()
            return

        if ver == "now":
            path = "%s/%s" % (app["dir"], file)
        else:
            path = "data/objs/%s/%s/%s" % (appid, ver, file)
        if os.path.exists(path):
            return open(path, "r")
        else:
            raise web.notfound()

