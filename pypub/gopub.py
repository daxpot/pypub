#coding=utf-8
import web
import json
from tools import WEB_T, CONFIG_T, COMMON
from pubcore import PubCore
import datetime
from synccore import SyncCore
import threading

def sync_app(appid):
    s = SyncCore()
    s.run(appid)

class Gopub(object):
    """docstring for Gopub"""
    def __init__(self):
        pass

    def merge_update(self, update, last_md5, key):
        key_list = []
        for file in update[key]:
            obj = {
                "file": file,
                "ver": "now"
            }
            if file in last_md5:
                obj["ver"] = last_md5[file]["ver"]
            key_list.append(obj)
        return key_list

    def get_infos(self):
        i = web.input()
        appid = i.get('appid')
        app = CONFIG_T.get_apps(appid)
        if app == None:
            return {}, " appid:%s 错误" % appid.encode("utf-8")
        pc = PubCore(app)
        update = pc.publish("now")
        last_md5 = pc.get_last_md5()
        infos = {
            "new": self.merge_update(update, last_md5, "new"),
            "del": self.merge_update(update, last_md5, "del"),
            "modify": self.merge_update(update, last_md5, "modify"),
            "appid": appid
        }

        curinfo = COMMON.dbget("cur-%s" % appid, None, "json")
        if curinfo and len(curinfo["history"])>=1:
            infos["lastver"] = curinfo["history"].pop()
        else:
            infos["lastver"] = "0.0.0"
        return infos, ""

    def render(self, errmsg):
        render = WEB_T.get_render()
        session = WEB_T.get_session()
        infos, errmsg2 = self.get_infos()
        errmsg = ("%s<br>%s" % (errmsg, errmsg2)).strip("<br>")
        return render.gopub(session.username, infos, errmsg)

    def GET(self):
        WEB_T.check_login()
        return self.render("")

    def check_post_param(self):
        i = web.input()
        appid = i.get('appid')
        version = i.get('version')
        comment = i.get('comment')
        app = CONFIG_T.get_apps(appid)
        if app == None:
            return "", "", "", "", [], "appid错误"
        if COMMON.check_version(version) == False:
            return "", "", "", "", [],"版本号必须为 '*.*.*' 。*为数字"
        db = COMMON.get_db()
        key = "ver-%s-%s" % (appid, version)
        if COMMON.dbget(key):
            return "", "", "", "", [],"该版本号已经存在"

        file_len = int(i.get("files-len"))
        files = []
        for j in range(1, file_len+1):
            file = i.get("files-%d" % j)
            if file:
                files.append(file)
        if len(files) == 0:
            return "", "", "", "", [],"必须选择至少一个文件"

        return appid, version, comment, files, app, ""

    def deal_post(self):
        appid, version, comment, files, app, errmsg = self.check_post_param()
        if errmsg:
            return errmsg

        pc = PubCore(app)
        update = pc.publish(version, files)
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
        return "发布成功,文件更新详情：%s" % json.dumps(update)


    def deal_fallback(self):
        i = web.input()
        appid = i.get("appid")
        version = i.get("version")
        if COMMON.check_version(version) == False:
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
