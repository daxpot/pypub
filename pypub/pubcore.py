#coding=utf-8
import os
from tools import WEB_T, CONFIG_T, COMMON
import json
import glob

class PubCore(object):
    """docstring for PubCore"""
    def __init__(self, app):
        self.appid = app["name"]
        self.dir = app["dir"].rstrip("/")
        if "remote_dir" in app:
            self.remote_dir = app["remote_dir"]

    def get_pubignore(self):
        try:
            with open("%s/.pypub/pubignore" % self.dir, "r") as f:
                pubignore = f.readlines()
        except:
            pubignore = []
        pubignore.append(".pypub/*")
        ignore_files = {}
        for f in pubignore:
            f = f.strip()
            if f:
                ret = glob.glob("%s/%s" % (self.dir, f))
                for i in ret:
                    ignore_files[i] = 1
        return ignore_files

    #获取项目当前的md5，注意pubignore
    def get_current_md5(self):
        cache_md5 = COMMON.dbget("cache-%s" % self.appid, {}, "json")
        file_map = {}
        file_md5 = {}
        ignore_files = self.get_pubignore()

        for parent, dirnames, filenames in os.walk(self.dir):

            for fn in filenames:
                full = os.path.join(parent, fn)
                if full in ignore_files:
                    continue
                file_name = full.replace(self.dir + "/", "")
                mtime = os.path.getmtime(full)
                if file_name in cache_md5 and "time" in cache_md5[file_name] and "md5" in cache_md5[file_name] and cache_md5[file_name]["time"] == mtime:
                    md5 = cache_md5[file_name]["md5"]
                else:
                    md5 = COMMON.get_file_md5(full)

                file_map[file_name] = md5
                file_md5[file_name] = {
                    "time": mtime,
                    "md5": md5
                }
        COMMON.dbput("cache-%s" % self.appid, file_md5, "json")
        return file_map

    #获取当前线上版本文件的md5
    def get_last_md5(self):
        appver = COMMON.dbget("cur-%s" % self.appid, {"current":""}, "json")
        version = appver["current"]
        md5 = COMMON.dbget("meta-%s-%s" % (self.appid, version), {}, "json")
        return md5

    def compute_update(self, last_md5, current_md5):
        pass

    def publish(self, version):
        last_md5 = self.get_last_md5()
        current_md5 = self.get_current_md5()
        print last_md5, current_md5
        update = self.compute_update(last_md5, current_md5)
        return {"new": ["file1"], "modify": [], "del": []}
