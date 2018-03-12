#coding=utf-8
import difflib
import web
import os
from tools import WEB_T, CONFIG_T, COMMON, RemoteApp

class Codediff(object):
    """docstring for Codediff"""
    def __init__(self):
        pass

    def render(self, errmsg, table):
        render = WEB_T.get_render()
        session = WEB_T.get_session()
        return render.codediff(session.username, errmsg, table)

    def get_path(self, file, ver, app):
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
            return path
        else:
            meta = COMMON.dbget("meta-%s-%s" % (app["name"], ver), {}, "json")
            if file in meta:
                ver = meta[file]["ver"]
                return "data/objs/%s/%s/%s" % (app["name"], ver, file)
        return None

    def check_post_param(self):
        i = web.input()
        appid = i.get('appid')
        file = i.get('src')
        v1 = i.get('v1')
        v2 = i.get("v2")

        app = CONFIG_T.get_apps(appid)
        if app == None:
            return "appid错误", None, None
        v1path = self.get_path(file, v1, app)
        v2path = self.get_path(file, v2, app)
        return None, v1path, v2path

    def read_file(self, path):
        if not self.istextfile(path):
            return ["二进制文件，无法对比"]
        try:
            with open(path, "r") as f:
                return f.readlines()
        except Exception as e:
            pass
        return []

    def istextfile(self, path):
        if not os.path.exists(path):
            return 1
        s = open(path).read()
        try:
            s.decode("utf-8")
            return 1
        except:
            return 0


    def GET(self):
        WEB_T.check_login()
        i = web.input()
        errmsg, v1path, v2path = self.check_post_param()
        if errmsg:
            return self.render(errmsg, "")
        diff = difflib.HtmlDiff()

        v1title = (u"<a href='downfile?appid=%s&ver=%s&src=%s'>下载%s</a>" % (i.get("appid"), i.get("v1"), i.get("src"), i.get("v1"))).encode("utf-8")
        v2title = (u"<a href='downfile?appid=%s&ver=%s&src=%s'>下载%s</a>" % (i.get("appid"), i.get("v2"), i.get("src"), i.get("v2"))).encode("utf-8")
        print v1path, v2path
        v1lines = self.read_file(v1path)
        v2lines = self.read_file(v2path)
        table = diff.make_table(v2lines, v1lines, v2title, v1title)
        return self.render("", table)