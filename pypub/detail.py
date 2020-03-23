#coding=utf-8
import web
import json
from .tools import WEB_T, CONFIG_T, COMMON
from .pubcore import PubCore
import datetime

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
            return {"vers": {}, "history": []}, "appid错误"
        page = i.get("page")
        try:
            page = int(page)
        except:
            page = 1
        appver.setdefault("history", [])
        infos = {"vers": {}, "history": appver["history"], "current": appver["current"], "page": page, "appid": appid}
        for ver in appver["history"]:
            key = "ver-%s-%s" % (appid, ver)
            infos["vers"][ver] = COMMON.dbget(key, None, "json")
        # infos["history"].append("now")
        # if page == 1:
        #     app = CONFIG_T.get_apps(appid)
        #     pc = PubCore(app)
        #     infos["vers"]["now"] = {
        #         "uptime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        #         "owner": "系统",
        #         "comment": "当前文件",
        #         "app": appid,
        #         "update": pc.publish("now")
        #     }

        infos["history"].reverse()
        start = (page-1)*20
        end = page*20
        count = len(infos["history"])

        for i in range(start, end):
            if i >= len(infos["history"]):
                break
            ver = infos["history"][i]
            verinfo = infos["vers"][ver]
            infos["vers"][ver]["newhtm"] = ""
            for file in verinfo["update"]["new"]:
                infos["vers"][ver]["newhtm"] += "<a href='codediff?appid=%s&src=%s&v1=%s&v2=now'>%s</a><br>" % (appid, file, ver, file)

            infos["vers"][ver]["modifyhtm"] = ""
            for file in verinfo["update"]["modify"]:
                v2 = 'now'
                for j in range(i+1, count):
                    v = infos["history"][j]
                    vinfo = infos["vers"][v]
                    if file in vinfo["update"]["new"] or file in vinfo["update"]["modify"]:
                        v2 = v
                        break
                infos["vers"][ver]["modifyhtm"] += "<a href='codediff?appid=%s&src=%s&v1=%s&v2=%s'>%s</a><br>" % (appid, file, ver, v2, file)
            
            infos["vers"][ver]["delhtm"] = ""
            for file in verinfo["update"]["del"]:
                v2 = "now"
                for j in range(i+1, count):
                    v = infos["history"][j]
                    vinfo = infos["vers"][v]
                    if file in vinfo["update"]["new"] or file in vinfo["update"]["modify"]:
                        v2 = v
                        break
                infos["vers"][ver]["delhtm"] += "<a href='codediff?appid=%s&src=%s&v1=%s&v2=%s'>%s</a><br>" % (appid, file, v2, 'now', file)

        infos["history"] = infos["history"][start:end]
        return infos, ""

    def GET(self):
        WEB_T.check_login()
        infos, errmsg = self.get_infos();
        return self.render(infos, errmsg)