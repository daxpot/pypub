#coding=utf-8
import sys
import commentjson
import os
import shutil
import errno
import stat
import logging
import time
from web.wsgiserver import CherryPyWSGIServer
import web
import hashlib
import leveldb
import json
import paramiko
import fnmatch

class ConfigT(object):
    def __init__(self):
        pass

    def load_config(self):
        config_path = "config.json"
        argv = COMMON.get_command_arg("-c")
        if argv:
            config_path = argv
        try:
            with open(config_path, "r") as f:
                return commentjson.loads(f.read())
        except Exception, e:
            logging.error(e)
        return False

    def load_ssl(self):
        config = self.load_config()
        if config and "certs" in config and "key" in config["certs"] and "pem" in config["certs"]:
            CherryPyWSGIServer.ssl_certificate = config["certs"]["pem"]
            CherryPyWSGIServer.ssl_private_key = config["certs"]["key"]

    def init_logger(self, logLevel=logging.INFO):
        log_root = 'data/log'
        if not os.path.exists(log_root):
            os.makedirs(log_root)
        cur_time = time.strftime("%Y%m%d", time.localtime())

        log_file_name = '%s/%s.log' %(log_root, cur_time)
        logging.basicConfig(level=logLevel,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=log_file_name,
                    filemode='a+')

        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s\t[%(levelname)s]\t%(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    def get_apps(self, appid=None):
        config = self.load_config()
        apps = []
        if "apps" in config:
            apps = config["apps"]
            for app in apps:
                if "dir" in app and "remote_dir" in app:
                    app.setdefault("name", os.path.basename(app["dir"]))
                    app.setdefault("from", "local")
                    app.setdefault("to", [])
                    app["name"] = app["name"].encode("utf-8")
                    app["remote_dir"] = app["remote_dir"].rstrip("/").encode("utf-8")
                    app["dir"] = app["dir"].rstrip("/").encode("utf-8")
                else:
                    apps.remove(app)
        if appid:
            app = None
            for item in apps:
                if item["name"] == appid:
                    return item
            return None
        return apps

    def get_servers(self, serverid=None):
        config = self.load_config()
        servers = {}
        if "servers" in config and isinstance(config["servers"], dict):
            for sid in config["servers"]:
                server = config["servers"][sid]
                if "host" in server and isinstance(server["host"], unicode) and server["host"] and "user" in server and isinstance(server["user"], unicode) and server["user"] and "password" in server and isinstance(server["password"], unicode) and server["password"]:
                    if "port" not in server or not isinstance(server["port"], int):
                        server["port"] = 22
                    server["id"] = sid
                    servers[sid] = server
        if serverid:
            if serverid.decode("utf-8") in servers:
                return servers[serverid]
        return servers



class WebT(object):
    def __init__(self):
        self.session = None
        self.web_render = web.template.render("templates", base="layout")

    def get_render(self):
        return self.web_render

    def check_login(self):
        session = self.get_session()
        if session.get("logged_in", False):
            return True
        else:
            raise web.seeother('/login')
            return False
    def get_session(self, app=None):
        if self.session:
            return self.session
        elif app:
            self.session = web.session.Session(app, web.session.DiskStore('data/sessions'))
            return self.session
        else:
            logging.error("获取session错误")
            return None

class Common(object):
    """docstring for Common"""
    def __init__(self):
        print "Common init"
        self.leveldb = None

    def get_command_arg(self, param):
        arg_len = len(sys.argv)
        for i in range(0, arg_len):
            if sys.argv[i] == param and (i+1)<arg_len:
                return sys.argv[i+1]
        return False


    def get_md5(self, s):
        return hashlib.md5(s).hexdigest()

    def get_file_md5(self, file):
        with open(file, "r") as f:
            return self.get_md5(f.read())

    def get_db(self):
        if not self.leveldb:
            self.leveldb = leveldb.LevelDB("data/leveldb", create_if_missing=True)
        return self.leveldb

    def dbget(self, key, default=None, format="string"):
        db = self.get_db()
        try:
            data = db.Get(key)
            if format == "json":
                data = json.loads(data)
            return data
        except KeyError:
            return default
    def dbput(self, key, value, format='string'):
        db = self.get_db()
        if format == "json":
            value = json.dumps(value)
        db.Put(key, value)


class RemoteApp(object):
    """docstring for AppFiles"""
    def __init__(self, app, serverid="local"):
        self.app = app
        self.serverid = serverid
        if serverid != "local":
            self.dir = app["remote_dir"]
            server = CONFIG_T.get_servers(serverid)
            if not server:
                msg = "%s 不在config.json中" % serverid
                logging.error(msg)
                raise msg
            logging.info("link %s", serverid)
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(server["host"], server["port"], server["user"], server["password"])
            self.sftp = paramiko.SFTPClient.from_transport(self.ssh.get_transport())
            self.sftp = self.ssh.open_sftp()
        else:
            self.dir = app["dir"]
            self.ssh = None
            self.sftp = None

    def __mkdirs(self, path):
        try:
            os.makedirs(path)
        except OSError as exc: 
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

    def get(self, src, dist):
        src = "%s/%s" % (self.dir, src)
        dist_dir = os.path.dirname(dist)
        self.__mkdirs(dist_dir)
        if self.serverid == "local":
            shutil.copy(src,  dist_dir)
        else:
            self.sftp.get(src, dist)

    def put(self, src, dist):
        dist = "%s/%s" % (self.dir, dist)
        dist_dir = os.path.dirname(dist)
        if self.serverid == "local":
            self.__mkdirs(dist_dir)
            shutil.copy(src, dist)
        else:
            stdin, stdout, stderr = self.ssh.exec_command("mkdir -p %s" % dist_dir)
            stdout.readlines()
            stderr.readlines()
            self.sftp.put(src, dist)

    def remove(self, dist):
        dist = "%s/%s" % (self.dir, dist)
        if self.serverid == "local":
            try:
                os.remove(dist)
            except Exception as e:
                logging.error(e)
        else:
            try:
                self.sftp.remove(dist)
            except Exception as e:
                logging.error(e)

    def file_md5(self, path):
        path = "%s/%s" % (self.dir, path)
        if self.serverid == "local":
            return COMMON.get_file_md5(path)
        else:
            stdin, stdout, stderr = self.ssh.exec_command("md5sum %s" % path)
            lines = stdout.readlines()
            if lines:
                md5 = lines[0].split(" ")[0]
                return md5
        return ""

    def __get_all_files_in_remote_dir(self, remote_dir):
        # 保存所有文件的列表
        all_files = {}

        # 去掉路径字符串最后的字符'/'，如果有的话
        if remote_dir[-1] == '/':
            remote_dir = remote_dir[0:-1]

        # 获取当前指定目录下的所有目录及文件，包含属性值
        try:
            files = self.sftp.listdir_attr(remote_dir)
        except IOError as e:
            return all_files
        for x in files:
            # remote_dir目录中每一个文件或目录的完整路径
            filename = remote_dir + '/' + x.filename
            # 如果是目录，则递归处理该目录，这里用到了stat库中的S_ISDIR方法，与linux中的宏的名字完全一致
            if stat.S_ISDIR(x.st_mode):
                # all_files.extend(self.__get_all_files_in_remote_dir(filename))
                files = self.__get_all_files_in_remote_dir(filename)
                for f in files:
                    all_files[f] = files[f]
            else:
                all_files[filename] = x.st_mtime
        return all_files

    def __check_ignore(self, filename, ignores):
        for ignore in ignores:
            ignore = ignore.strip()
            if ignore and fnmatch.fnmatch(filename, ignore):
                return True
        return False

    def __get_ignores(self):
        path = "data/objs/%s/pubignore" % self.app["name"]
        ignores = []
        try:
            self.get(".pypub/pubignore", path)
            with open(path, "r") as f:
                ignores = f.read().split("\n")
        except Exception as e:
            logging.error(e)
        return ignores

    def get_md5s(self):
        ignores = self.__get_ignores()
        key = "server-%s-%s" % (self.app["name"], self.serverid)
        cache_md5 = COMMON.dbget(key, {}, "json")
        if self.serverid == "local":
            abs_files = {}
            for parent, dirnames, filenames in os.walk(self.dir):
                for fn in filenames:
                    full = os.path.join(parent, fn)
                    mtime = os.path.getmtime(full)
                    abs_files[full] = mtime
        else:
            abs_files = self.__get_all_files_in_remote_dir(self.dir)

        new_cache_md5 = {}
        for abs_f in abs_files:
            filename = abs_f.replace(self.dir + "/", "")
            filename = filename.decode("utf-8")
            if filename.find(".pypub") != 0 and not self.__check_ignore(filename, ignores):
                if filename in cache_md5 and cache_md5[filename]["time"] == abs_files[abs_f]:
                    md5 = cache_md5[filename]["md5"]
                else:
                    md5 = self.file_md5(filename)
                new_cache_md5[filename] = {
                    "md5": md5,
                    "time": abs_files[abs_f]
                }
        COMMON.dbput(key, new_cache_md5, "json")
        return new_cache_md5
    def close(self):
        if self.serverid != "local":
            self.sftp.close()
            self.ssh.close()

        

COMMON = Common()
WEB_T = WebT()
CONFIG_T = ConfigT()
