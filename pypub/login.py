#coding=utf-8
import web
from common import COMMON

class Login(object):
    """docstring for Login"""
    def __init__(self):
        self.session = COMMON.get_session()

    def GET(self):
        render = COMMON.get_render()
        self.session.logged_in = False
        return render.login("")

    def POST(self):
        i = web.input()
        username = i.get('username')
        password = i.get('password')
        password = COMMON.get_md5(password)
        config = COMMON.load_config()
        if username in config["users"] and password == config["users"][username]["password"]:
            self.session.logged_in = True
            self.session.username = username
            raise web.seeother('/')
        else:
            render = COMMON.get_render()
            return render.login("用户名或密码错误！")
