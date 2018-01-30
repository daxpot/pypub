#coding=utf-8
import paramiko
import logging
import stat
import os
import datetime
import logging
#同步项目代码到各个服务器中

from tools import WEB_T, CONFIG_T, COMMON

class Sync(object):
    """docstring for Sync"""
    def __init__(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sftp = None

    def link_server(self, server):
        try:
            self.ssh.close()
            self.ssh.connect(server["host"], server["port"], server["user"], server["password"])
            self.sftp = paramiko.SFTPClient.from_transport(self.ssh.get_transport())
            self.sftp = self.ssh.open_sftp()
            logging.info("%s %s", "link", server["host"])
            return True
        except Exception, e:
            logging.error(str(e))
            return False
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

    def get_server_files(self, app, server):
        remote_dir = app["remote_dir"]

        key = "server-%s-%s" % (app["name"], server["host"])
        cache_files = COMMON.dbget(key, {}, "json")
        new_cache_files = {}

        abs_files = self.__get_all_files_in_remote_dir(remote_dir)
        files = {}
        for abs_f in abs_files:
            f = abs_f.replace(remote_dir + "/", "")
            mtime = abs_files[abs_f]
            if f in cache_files and cache_files[f]["time"] == mtime:
                files[f] = cache_files[f]["md5"]
                new_cache_files[f] = cache_files[f]
            else:
                stdin, stdout, stderr = self.ssh.exec_command("md5sum %s" % abs_f)
                lines = stdout.readlines()
                if lines:
                    md5 = lines[0].split(" ")[0]
                    new_cache_files[f] = {
                        "md5": md5,
                        "time": mtime
                    }
                    files[f] = md5
        COMMON.dbput(key, new_cache_files, "json")
        return files

    def sync(self, app, server):
        if "remote_dir" not in app:
            app["remote_dir"] = "%s/%s" % (server["remote_root"], app["name"])
        s_files = self.get_server_files(app, server)
        cur = COMMON.dbget("cur-%s" % app["name"], {"current":""}, "json")
        current = cur["current"]
        meta = COMMON.dbget("meta-%s-%s" % (app["name"], current), {}, "json")
        for file in meta:
            ver = meta[file]["ver"]
            md5 = meta[file]["md5"]
            if file not in s_files or s_files[file] != md5:
                logging.info("%s %s", u"更新", file)
                localpath = "data/objs/%s/%s/%s" % (app["name"], ver, file)
                serverpath = "%s/%s" % (app["remote_dir"], file)
                serverdir = os.path.dirname(serverpath)
                try:
                    stdin, stdout, stderr = self.ssh.exec_command("mkdir -p %s" % serverdir)
                    stdout.readlines()
                    stderr.readlines()
                    self.sftp.put(localpath, serverpath)
                except Exception as e:
                    logging.error(e)
        for file in s_files:
            if file not in meta:
                logging.info("%s %s", u"删除", file)
                serverpath = "%s/%s" % (app["remote_dir"], file)
                try:
                    self.sftp.remove(serverpath)
                except Exception as e:
                    logging.error(e)
        COMMON.dbput("remote-%s-%s" % (app["name"], server["host"]), {
            "ver": current, 
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, "json")
        logging.info("%s %s", app["name"], current)

    def run(self):
        apps = CONFIG_T.get_apps()
        servers = CONFIG_T.get_servers()
        for server in servers:
            if self.link_server(server):
                for app in apps:
                    self.sync(app, server)
                self.ssh.close()


if __name__ == '__main__':
    CONFIG_T.init_logger()
    s = Sync()
    s.run()
