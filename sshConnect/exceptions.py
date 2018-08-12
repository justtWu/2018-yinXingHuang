#coding=utf-8
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


handler = logging.FileHandler('log.txt')
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s  %(name)s  [%(levelname)s]  %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)


class MyException(Exception):
	def __init__(self,message):
		self.message = message

class LoginException(MyException):
	def __init__(self,ip):
		super().__init__("Login Error")
		#TODO 是否要记录连接失败原因？比如是超时还是密码错误？若是有超时情况是否需要在连接模块加上超时设置？
		self.ip = ip
		logger.error("Login Error. ip:%s"%ip)
#TODO 还有哪些错误需要总结归纳出来
