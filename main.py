#coding=utf-8
session = None
import web
from pypub.tools import CONFIG_T, WEB_T
from pypub.index import Index
from pypub.login import Login
from pypub.detail import Detail

def main():
	global session
	config = CONFIG_T.load_config()
	if not config:
		print("配置文件加载失败！")
		return
	CONFIG_T.init_logger()
	CONFIG_T.load_ssl()
	urls = (
		"/", "Index",
		"/detail", "Detail",
		"/login", "Login"
		)
	web.config.debug = False
	app = web.application(urls, globals())
	session = WEB_T.get_session(app)
	app.run()

if __name__ == '__main__':
	main()