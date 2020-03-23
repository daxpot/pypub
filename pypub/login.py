#coding=utf-8
import web
from .tools import COMMON, WEB_T, CONFIG_T

class Login(object):
    """docstring for Login"""
    def __init__(self):
        self.session = WEB_T.get_session()

    def GET(self):
        render = WEB_T.get_render()
        self.session.logged_in = False
        return render.login("")

    def POST(self):
        i = web.input()
        username = i.get('username')
        password = i.get('password')
        password = COMMON.get_md5(password)
        config = CONFIG_T.load_config()
        if username in config["users"] and password == config["users"][username]["password"]:
            self.session.logged_in = True
            self.session.username = username
            raise web.seeother('/')
        else:
            render = WEB_T.get_render()
            return render.login("用户名或密码错误！")
