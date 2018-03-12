#coding=utf-8
import web
import json
from tools import WEB_T, CONFIG_T, COMMON
from pubcore import PubCore
import re
import datetime
from synccore import SyncCore
import threading

def sync_app(appid):
    s = SyncCore()
    s.run(appid)

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
            if "uptime" in info:
                info["uptime"] = info["uptime"]
            else:
                info["uptime"] = ver_info["uptime"]
            info["comment"] = ver_info["comment"]
            info["appid"] = appid
            info["version"] = info["current"]
            infos.append(info)
        infos = sorted(infos, cmp=lambda x,y:cmp(y["uptime"],x["uptime"]))
        return infos

    def render(self, errmsg):
        render = WEB_T.get_render()
        currrent_infos = self.get_infos()
        session = WEB_T.get_session()
        return render.index(session.username, currrent_infos, errmsg)

    def GET(self):
        WEB_T.check_login()
        return self.render("")

    def check_version(self, version):
        if re.match(r"^([0-9]+\.[0-9]+\.[0-9]+)$", version) == None:
            return False
        return True

    def check_post_param(self):
        i = web.input()
        appid = i.get('appid')
        version = i.get('version')
        comment = i.get('comment')
        app = CONFIG_T.get_apps(appid)
        if app == None:
            return "", "", "", "", "appid错误"
        if self.check_version(version) == False:
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
        t = threading.Thread(target=sync_app, args=(appid, ))
        t.start()
        return "发布成功"

    def deal_fallback(self):
        i = web.input()
        appid = i.get("appid")
        version = i.get("version")
        if self.check_version(version) == False:
            return '{"errcode": 1, "errmsg": "版本号必须为 \'*.*.*\' 。*为数字"}'
        app = CONFIG_T.get_apps(appid)
        if not app:
            return '{"errcode": 1, "errmsg": "app不存在"}'
        pc = PubCore(app)
        data = pc.fallback(version)
        t = threading.Thread(target=sync_app, args=(appid, ))
        t.start()
        return json.dumps(data)

    def POST(self):
        WEB_T.check_login()
        i = web.input()
        if i.get("action") == "fallback":
            data = self.deal_fallback()
            return data
        else:
            errmsg = self.deal_post()
            return self.render(errmsg)
        