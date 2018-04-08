#coding=utf-8
import web
from tools import WEB_T, CONFIG_T, COMMON
from synccore import SyncCore
import threading

def sync_app(appid=None, host=None):
    s = SyncCore()
    s.run(appid, host)

class Syncdetail(object):
    """docstring for Syncdetail"""
    def __init__(self):
        pass

    def get_infos(self):
        i = web.input()
        appid = i.get("appid")
        if appid:
            app = CONFIG_T.get_apps(appid)
            apps = [app]
        else:
            apps = CONFIG_T.get_apps()
        infos = []
        for app in apps:
            for sid in app["to"]:
                key = "remote-%s-%s" % (app["name"], sid)
                info = COMMON.dbget(key, None, "json")
                if info:
                    infos.append({
                        "appid": app["name"],
                        "host": sid,
                        "ver": info["ver"],
                        "time": info["time"]
                    })

        return infos

    def render(self, errmsg):
        render = WEB_T.get_render()
        infos = self.get_infos()
        session = WEB_T.get_session()
        return render.syncdetail(session.username, infos, errmsg)

    def GET(self):
        WEB_T.check_login()
        return self.render("");

    def POST(self):
        WEB_T.check_login()
        i = web.input()
        appid = i.get("appid")
        host = i.get("host")
        t = threading.Thread(target=sync_app, args=(appid, host))
        t.start()
        return self.render("提交同步成功");

        