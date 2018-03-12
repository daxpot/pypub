#coding=utf-8
import os
from tools import WEB_T, CONFIG_T, COMMON, RemoteApp
import json
import errno
import datetime
import shutil

class PubCore(object):
    """docstring for PubCore"""
    def __init__(self, app):
        self.app = app
        self.appid = app["name"]
        self.dir = app["dir"]
        self.remote_dir = app["remote_dir"]
        self.ra = RemoteApp(app, app["from"], app["dir"])

    #获取当前线上版本文件的md5
    def get_last_md5(self):
        appver = COMMON.dbget("cur-%s" % self.appid, {"current":""}, "json")
        version = appver["current"]
        md5 = COMMON.dbget("meta-%s-%s" % (self.appid, version), {}, "json")
        return md5

    def __mkdirs(self, path):
        try:
            os.makedirs(path)
        except OSError as exc: 
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

    def compute_update(self, last_md5, current_md5, version):
        update = {"new": [], "modify": [], "del": []}
        objs_path = "./data/objs/%s/%s" % (self.appid, version)
        try:
            shutil.rmtree(objs_path)
        except:
            pass
        self.__mkdirs(objs_path)
        meta = {}
        for file in current_md5:
            if file not in last_md5:
                update["new"].append(file)
                meta[file] = {
                    "md5": current_md5[file]["md5"],
                    "ver": version
                }
                self.ra.get(file, "%s/%s" % (objs_path, file))
            elif last_md5[file]["md5"] != current_md5[file]["md5"]:
                update["modify"].append(file)
                meta[file] = {
                    "md5": current_md5[file]["md5"],
                    "ver": version
                }
                self.ra.get(file, "%s/%s" % (objs_path, file))
            else:
                meta[file] = last_md5[file]
        for file in last_md5:
            if file not in current_md5:
                update["del"].append(file)
        return update, meta

    def publish(self, version):
        version = version.encode("utf-8")
        last_md5 = self.get_last_md5()
        current_md5 = self.ra.get_md5s()
        update, meta = self.compute_update(last_md5, current_md5, version)
        COMMON.dbput("meta-%s-%s" % (self.appid, version), meta, "json")
        return update

    def compute_fallback(self, version_md5, current_md5, version):
        for file in version_md5:
            if file not in current_md5 or current_md5[file]["md5"] != version_md5[file]["md5"]:
                file_path = "./data/objs/%s/%s/%s" % (self.appid, version_md5[file]["ver"], file)
                self.ra.put(file_path, file)
        for file in current_md5:
            if file not in version_md5:
                self.ra.remove(file)
        curinfo = COMMON.dbget("cur-%s" % self.appid, {"history": []}, "json")
        curinfo["current"] = version
        curinfo["uptime"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        COMMON.dbput("cur-%s" % self.appid, curinfo, "json")

    def fallback(self, version):
        version = version.encode("utf-8")
        version_md5 = COMMON.dbget("meta-%s-%s" % (self.appid, version), None, "json")
        if not version_md5:
            return {"errcode": 1, "errmsg": "版本meta信息不存在"}
        current_md5 = self.ra.get_md5s()
        self.compute_fallback(version_md5, current_md5, version)
        return {"errcode": 0}
