# pypub
python3 发布项目到多个服务器
特点:
1. 将文件夹视为项目名称，管理项目代码即管理该文件夹代码
2. 支持部署项目到多个服务器
3. 支持项目版本管理，包括发布、回退
4. 支持查看版本文件详情，对比不同版本文件
5. 支持查看各服务器同步项目情况
6. 支持服务器同步完项目版本后执行钩子程序(.pypub/hooks.sh, 详情查看testapp/app1/.pypub/hooks.sh)
7. 支持忽略发布指定文件(.pypub/pubignore, 详情查看testapp/app1/.pypub/pubignore)
8. 项目来源支持来自于其他服务器

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
			"permission": 2			//暂定权限值0, 1, 2,暂时没用
		}
	},
	"apps": [
		{
			"name": "app1",				//默认为项目目录名称
			"dir": "./testapp/app1",
			"remote_dir": "/www/app1/", //项目部署到远程服务器的目录
			"from": "local",			//默认为local，local代表项目在本地，也可以配置为其他服务器
			"to": ["server1", "server2"]//项目需要部署到哪些服务器上
		},
		{
			"dir": "/app2",
			"remote_dir": "/www/app2",
			"from": "server1",
			"to": ["server1", "local"] //部署也可以是从远程服务器发布到本地
		}
	],
	"servers": {
		//远程服务器配置, local代表本机
		"server1": {
			"host": "server1.example.cn",
			"user": "user",
			"password": "password",
			"port": 22
		},
		"server2": {
			"host": "server2.example.cn",
			"user": "user",
			"password": "password",
			"port": 22
		}
	}
}
```
配置好之后执行python3 main.py
正式环境python3 main.py 8080 2>nohup.out &
输入127.0.0.1:8080进入版本发布管理后台
