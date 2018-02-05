<pre>
key 				value

cur-$appid  		json example
					{
						"current": "1.0.1",							//当前版本ID
						"history":["0.0.1", "0.1.2", "0.1.5"]						//历史版本的版本ID
					}
ver-$appid-$ver		json example
					{
						"app": "demo",						//所属app
						"uptime": "2017-01-03 16:00:00",	//发布时间
						"comment": "备注",
						"update": {"new": ["a.txt", "b.txt"], "modify": [], "del": []}		//更新的文件
					}

meta-$appid-$ver    json example
					{
						"file1": {
							"md5": "asdfasdf",	//文件file1在version版本的md5
							"ver": "0.0.1"		//文件file1存储的位置
						},
						...
					}

server-$appid-$serverid json example
					{
						"file1": {
							"md5": "asdf", //文件file1缓存的md5
							"time":"1232" //缓存md5时对应的文件的修改时间
						}
					}
remote-$appid-$serverid json example
					{
						"ver": "0.0.1",
						"time": "2018-01-30 12:27:22"
					}
</pre>