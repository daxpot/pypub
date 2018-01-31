# pypub
python 发布项目到多个服务器
特点:
	1. 将文件夹视为项目名称，管理项目代码即管理该文件夹代码
	2. 支持同步项目到多个服务器
	3. 支持项目版本管理，包括发布、回退
	4. 支持查看版本文件详情，对比不同版本文件
	5. 支持查看各服务器同步项目情况
	6. 支持服务器同步完项目版本后执行钩子程序(.pypub/hooks.sh, 详情查看testapp/app1/.pypub/hooks.sh)
	7. 支持忽略发布指定文件(.pypub/pubignore, 详情查看testapp/app1/.pypub/pubignore)

使用方法:
配置config.json
示例
```json
{
	"certs":{			//pypub支持https
		"key": "certs/test.key",
		"pem": "certs/test.pem"
	},
	"users": {			//后台管理用户
		"test": {
			"password": "password md5",
			"permission": 2			//暂定权限值0, 1, 2	忽略
		}
	},
	"apps_root": "./testapp",
	"apps": [
		//默认会自动识别apps_root目录下的所有文件夹为app
		{
			"dir": "./testapp/app1",
			"remote_dir": "/www/app1/" //默认为 remote_root/name，app在远程服务器的目录选择原则，remote_dir>servers中配置的remote_root>顶层配置的remote_root
		}
	],
	"remote_root": "/www",
	"servers": [
		//配置需要部署的远程服务器
		{
			"host": "host1.example.cn",
			"user": "user",
			"password": "password",
			"port": 22,
			"remote_root": "/pypub"		//覆盖上层设置的remote_root，不设置则默认为上层设置的remote_root，即默认为/www，不同服务器可设置不同的remote_root
		},
		...
	]
}
```
配置好之后执行python main.py
输入127.0.0.1:8080进入版本发布管理后台