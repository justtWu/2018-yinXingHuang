#coding=utf-8
RESULT_FILE = './sshResult.csv'    #最终显示结果的表格
IP_FILE = './files/ipConfig.txt'  #一个服务器占一行，ip，用户以及密码之间用逗号隔开
CMD_FILE = './files/cmdConfig.txt'#一个列名对应一个命令，增加或者删除一列都要同时增加或者删除列名以及命令，每一项之间一个英文逗号隔开,sudo的问题代码中已解决，如果有交互写y之类的，请在命令结尾加上-y
RETRY_FILE = './files/retry.txt'   #重试密码之间一个英文逗号隔开
SSH_LOG_FILE = './files/sshLog.txt'#日志文件

