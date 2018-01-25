#coding=utf-8
session = None
import web
from pypub.common import COMMON
from pypub.index import Index
from pypub.login import Login

def main():
	global session
	config = COMMON.load_config()
	if not config:
		print("配置文件加载失败！")
		return
	COMMON.load_ssl(config)
	urls = (
		"/", "Index",
		"/login", "Login"
		)
	web.config.debug = False
	app = web.application(urls, globals())
	session = COMMON.get_session(app)
	app.run()

if __name__ == '__main__':
	main()