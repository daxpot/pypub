#coding=utf-8
import web
import sys
import os
from pypub import CONFIG_T, WEB_T
from pypub import Index, Login, Detail, Codediff, Downfile, Syncdetail, Gopub
from web.wsgiserver import CherryPyWSGIServer

def main():
    config = CONFIG_T.load_config()
    if not config:
        print("配置文件加载失败！")
        return
    CONFIG_T.init_logger()
    CONFIG_T.load_ssl(CherryPyWSGIServer)
    urls = (
        "/", "Index",
        "/detail", "Detail",
        "/login", "Login",
        "/codediff", "Codediff",
        "/downfile", "Downfile",
        "/syncdetail", "Syncdetail",
        "/gopub", "Gopub"
        )
    web.config.debug = False
    app = web.application(urls, globals())
    session = WEB_T.get_session(app)
    app.run()

if __name__ == '__main__':

    if 'daemon' in sys.argv[1:]:
        pid = os.fork()
        if pid != 0 : quit()

    main()