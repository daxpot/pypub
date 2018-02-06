#coding=utf-8
import web
import os
from tools import WEB_T, CONFIG_T, COMMON, RemoteApp

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
            ra = RemoteApp(app, app["from"], app["dir"])
            path = "data/objs/%s/now/%s" % (app["name"], file)
            try:
                ra.get(file, path)
            except Exception as e:
                try:
                    os.remove(path)
                except:
                    pass
        else:
            path = "data/objs/%s/%s/%s" % (appid, ver, file)

        web.header("Content-type", "application/octet-stream")
        web.header("Content-Disposition", "attachment;filename='%s'" % os.path.basename(path));

        if os.path.exists(path):
            return open(path, "r")
        else:
            raise web.notfound()

