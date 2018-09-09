#coding=utf-8
import os
from config import configs
def _set_env():
	"""
	设置环境变量
	"""
	cwd = os.getcwd()
	for key,value in configs.items():
		if key.find("FILE") != -1:
			os.environ[key] = os.path.join(cwd,value)
		else:
			if type(value) is not str:
				value = str(value)
			os.environ[key] = value
_set_env()

import sys,getopt
from ssh_connect.sshLogDeal import loggerForSsh
from ssh_connect.pid import pid_handler
from ssh_connect.connect import run

def help():
	print "Usages:\npython setup -s start|stop|restart.\npython setup --start | --stop | --restart"

def start(restart=False):
	if not restart: 
		loggerForSsh.info("*****Service start*****")
	pid_handler.write_pid()
	run()

def stop(restart=False):
	status = pid_handler.kill()
	if not status:
		return
	if not restart:
		loggerForSsh.info("*****Service stop*****")

def restart():
	stop(restart=True)
	start(restart=True)
	loggerForSsh.info("*****Service restart*****")


def main(argvs):
	try:
		opts,args = getopt.getopt(argvs, "s:", longopts=["start","stop","restart","help"])
	except getopt.GetoptError as e:
		help()
		sys.exit(1)
	for opt,argv in opts:
		if (opt=='-s' and argv=='start') or opt=='--start':
			start()
		elif (opt=='-s' and argv=='stop') or opt=='--stop':
			stop()
		elif (opt=='-s' and argv=='restart' or opt=='--restart'):
			restart()
		elif opt=='--help':
			help()
 
if __name__ == "__main__":
	main(sys.argv[1:])