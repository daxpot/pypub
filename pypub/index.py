#coding=utf-8
import web
import json
from .tools import WEB_T, CONFIG_T, COMMON
import datetime
from functools import cmp_to_key
def cmp(a, b):
    return (a > b) - (a < b) 

class Index(object):
    """docstring for Index"""
    def __init__(self):
        pass

    def db_read_json(self, key, default=None):
        data = COMMON.dbget(key, {}, "json")
        if default:
            for k in default:
                data.setdefault(k, default[k])
        return data

    def get_infos(self):
        apps = CONFIG_T.get_apps()
        db = COMMON.get_db()
        infos = []
        for app in apps:
            appid = app["name"]
            info = self.db_read_json("cur-%s" % appid, {"current": ""})
            ver_info = self.db_read_json("ver-%s-%s" % (appid, info["current"]), {"uptime": "", "comment": ""})
            info["uptime"] = ver_info["uptime"]
            info["comment"] = ver_info["comment"]
            info["appid"] = appid
            info["version"] = info["current"]
            infos.append(info)
        infos = sorted(infos, key=cmp_to_key(lambda x,y:cmp(y["uptime"],x["uptime"])))
        return infos

    def render(self, errmsg):
        render = WEB_T.get_render()
        currrent_infos = self.get_infos()
        session = WEB_T.get_session()
        return render.index(session.username, currrent_infos, errmsg)

    def GET(self):
        WEB_T.check_login()
        return self.render("")


        