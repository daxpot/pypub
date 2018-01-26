#coding=utf-8
import web
import json
from tools import WEB_T, CONFIG_T, COMMON
from pubcore import PubCore
import re
import datetime

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
        return infos

    def render(self, errmsg):
        render = WEB_T.get_render()
        currrent_infos = self.get_infos()
        session = WEB_T.get_session()
        return render.index(session.username, currrent_infos, errmsg)

    def GET(self):
        WEB_T.check_login()
        return self.render("")

    def check_post_param(self):
        i = web.input()
        appid = i.get('appid')
        version = i.get('version')
        comment = i.get('comment')
        apps = CONFIG_T.get_apps()
        app = None
        for item in apps:
            if item["name"] == appid:
                app = item
                break
        if app == None:
            return "", "", "", "", "appid错误"
        if re.match(r"^([0-9]+\.[0-9]+\.[0-9]+)$", version) == None:
            return "", "", "", "","版本号必须为 '*.*.*' 。*为数字"
        db = COMMON.get_db()
        key = "ver-%s-%s" % (appid, version)
        if COMMON.dbget(key):
            return "", "", "", "","该版本号已经存在"
        return appid, version, comment, app, None


    def deal_post(self):
        appid, version, comment, app, errmsg = self.check_post_param()
        if errmsg:
            return errmsg

        pc = PubCore(app)
        update = pc.publish(version)
        if not update:
            return "发布代码失败"
        verinfo = {
            "app" : appid,
            "version" : version,
            "uptime" : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "comment" : comment,
            "update" : update,
            "owner" : WEB_T.get_session().username
        }
        db = COMMON.get_db()
        key = "ver-%s-%s" % (appid, version)
        db.Put(key, json.dumps(verinfo))
        appver = COMMON.dbget("cur-%s" % appid, {}, "json")
        appver.setdefault("history", [])
        appver["current"] = version
        appver["history"].append(version)
        db.Put("cur-%s" % appid, json.dumps(appver))
        return "发布成功"

    def POST(self):
        WEB_T.check_login()
        errmsg = self.deal_post()
        return self.render(errmsg)
        