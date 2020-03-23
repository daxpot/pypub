#coding=utf-8
import paramiko
import logging
import stat
import os
import datetime
import logging
#同步项目代码到各个服务器中

from .tools import WEB_T, CONFIG_T, COMMON, RemoteApp

class SyncCore(object):
    """docstring for SyncCore"""
    def __init__(self):
        pass

    def sync(self, app, serverid):
        ra_local = RemoteApp(app, app["from"], app["dir"])
        ignores = ra_local.get_ignores()
        ra_remote = RemoteApp(app, serverid, app["remote_dir"])
        s_files = ra_remote.get_md5s(ignores)
        cur = COMMON.dbget("cur-%s" % app["name"], {"current":""}, "json")
        current = cur["current"]
        meta = COMMON.dbget("meta-%s-%s" % (app["name"], current), {}, "json")
        bupdate = False
        for file in meta:
            ver = meta[file]["ver"]
            md5 = meta[file]["md5"]
            if file not in s_files or s_files[file]["md5"] != md5:
                logging.info("%s %s", u"更新", file)
                bupdate = True
                localpath = "data/objs/%s/%s/%s" % (app["name"], ver, file)
                ra_remote.put(localpath, file)
        for file in s_files:
            if file not in meta:
                logging.info("%s %s", u"删除", file)
                bupdate = True
                ra_remote.remove(file)
        hooks_local = "data/objs/%s/hooks.sh" % app["name"]
        try:
            ra_local.get(".pypub/hooks.sh", hooks_local)
            if bupdate and os.path.exists(hooks_local):
                spath = "/%s_%s.sh" % (app["name"], current)
                ra_remote.put(hooks_local, spath, False)
                stdin, stdout, stderr = ra_remote.exec_command("sh %s" % spath)
                while True:
                    try:
                        r = stderr.next()
                        if r.strip():
                            logging.error(r)
                    except:
                        break
                while True:
                    try:
                        r = stdout.next()
                        if r.strip():
                            logging.info(r)
                    except:
                        break
                ra_remote.remove(spath, False)
            os.remove(hooks_local)
        except Exception as e:
            logging.error(e)

        COMMON.dbput("remote-%s-%s" % (app["name"], serverid), {
            "ver": current, 
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, "json")
        logging.info("%s %s", app["name"], current)

    def run(self, appid=None, serverid=None):
        apps = CONFIG_T.get_apps(appid)
        if appid:
            apps = [apps]

        for app in apps:
            for sid in app["to"]:
                if serverid:
                    if serverid == sid:
                        self.sync(app, sid)
                else:
                    self.sync(app, sid)


if __name__ == '__main__':
    CONFIG_T.init_logger()
    s = SyncCore()
    s.run("app1")
