import sys
import commentjson
import os
import logging
import time

class Common(object):
	"""docstring for Common"""
	def __init__(self):
		pass

	def init_logger(self, logLevel):
	    log_root = 'log'
	    if not os.path.exists(log_root):
	        os.makedirs(log_root)
	    cur_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())

	    log_file_name = '%s/%s.log' %(log_root, cur_time)
	    logging.basicConfig(level=logLevel,
	                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
	                datefmt='%a, %d %b %Y %H:%M:%S',
	                filename=log_file_name,
	                filemode='w')

	    console = logging.StreamHandler()
	    console.setLevel(logging.DEBUG)
	    formatter = logging.Formatter('%(asctime)s\t[%(levelname)s]\t%(message)s')
	    console.setFormatter(formatter)
	    logging.getLogger('').addHandler(console)

	def get_command_arg(self, param):
		arg_len = len(sys.argv)
		for i in range(0, arg_len):
			if sys.argv[i] == param and (i+1)<arg_len:
				return sys.argv[i+1]
		return False


	def load_config(self):
		config_path = "config.json"
		argv = self.get_command_arg("-c")
		if argv:
			config_path = argv
		try:
			with open(config_path, "r") as f:
				return commentjson.loads(f.read())
		except Exception, e:
			logging.error(e)
		return False


TOOLS_COMMON = Common()
