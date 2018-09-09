#coding=utf-8
import os
from sshLogDeal import loggerForSsh


class Pid_handler(object):
	"""
	用于处理程序运行时的进程号(pid)的类
	"""
	def __init__(self,file):
		#file pid文件
		self.file = file

	def get_pid(self):
		"""
		输入：无
		输出：pid(得到了pid); None(未得到pid)
		功能：获取pid文件中的进程号
		"""
		try:
			with open(self.file,"r") as f:
				pid = f.read()
			return pid
		except IOError as e:
			loggerForSsh.error(u"读取pid文件失败")
			return None

	def write_pid(self):
		"""
		输入：无
		输出：布尔值，是否已经写入进程号
		功能：给pid文件写入进程号
		"""
		try:
			with open(self.file,"w") as f:
				f.write(str(os.getpid()))
			return True
		except IOError as e:
			loggerForSsh.error(u"写入pid文件失败")
			return False

	def kill(self):
		"""
		输入：无
		输出：返回布尔值，若成功为True,反之False
		功能：执行系统命令
		"""
		pid = self.get_pid()
		if pid is None:
			return False
		s = os.popen("taskkill /F /pid %s"%self.get_pid())
		if len(s.read()) > 0:
			loggerForSsh.info(s.read())
			return True
		else:
			loggerForSsh.info(u"杀死进程失败，进程不存在")
			return False

pid_handler = Pid_handler(os.environ["PID_FILE"])
