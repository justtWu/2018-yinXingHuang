
import paramiko
import time

from IO import reader,writer
from constants import LINE_SPLITER
from exceptions import logger

class baseConnecter(object):
    #连接基类，构造基本连接的配置信息
    def __init__(self,ip,userName,passWord):
        self.ip=ip
        self.userName=userName
        self.passWord=passWord
        self.port=22
        self.conStatus=False
class ssh_connecter(baseConnecter):
    '''
    建立连接，并完成一系列操作
    '''
    def __init__(self,ip,userName,passWord):
        super().__init__(ip,userName,passWord)
        self.sh=paramiko.SSHClient()
        self.ssh = None

    #进行连接并处理异常
    def get_connect(self,retryList):
        #允许连接不在know_hosts文件中的主机。
        self.sh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #用原始密码连接做第一次尝试
        try:
            self.sh.connect(self.ip, self.port, self.userName, self.passWord,timeout=3)
            self.conStatus=True
        except Exception as e:
            err=str(e)
            if 'Authentication failed' in err:
                print('身份验证失败，重试密码中......')
            elif '[WinError 10060]' in err:
                #print('连接超时无答复，'+self.ip+'主机未开或网络出现问题')#需要特别反应
                logger.error("%s连接超时，目标主机未开或网络出现问题"%self.ip)

        #若第一次尝试失败，进行密码重试
        if self.conStatus is False:
            for rePass in retryList:
                try:
                    self.sh.connect(self.ip, self.port, self.userName, rePass)
                    self.conStatus=True
                    #更新配置文件中的password
                    wt=writer()
                    wt.updete_json(ip=self.ip,password=rePass,passAlter=True)
                    break
                except Exception as e:
                    err2=str(e)
                    if err2 != '':
                        continue

        #若尝试完所有密码还是连接失败
        if self.conStatus is False:
            logger.error('%s试完所有密码未能连接成功'%self.ip)
        else:
            self.ssh=self.sh.invoke_shell()

    #写入命令
    def writeCommand(self,cmd):
        if self.conStatus == True:
            time.sleep(1)
            self.ssh.send(cmd+'\n')
            buf = self.ssh.recv(204800)
            return buf

    #解析结果
    def parse_result(self,string):
        if type(string) is not str:
            s = string.decode("utf-8")
        tmp = s.split(LINE_SPLITER)
        s = LINE_SPLITER.join(tmp[1:-1])
        return s

    #执行一系列命令
    def do(self,cmds):
        finalResult=[]
        for cmd in cmds:
            result=self.writeCommand(cmd)
            parsedResult=self.parse_result(result)
            finalResult.append(parsedResult)
        del finalResult[0]
        return finalResult



if __name__ == '__main__':
    logger.info("查看一次服务器信息")
    wd=reader()
    wt=writer()
    connect_info=wd.reader_connect()
    cmds=['lsb_release -a','who | grep \'([1-9]\' | awk \'{print $NF}\'','users','lscpu |grep \'Socket\' |awk \'{print $NF}\'','free -h','exit']
    showResult = []
    for j in connect_info:
        #print(j)
        get = []
        get.append(j['ip'])
        get.append(j['user'])
        get.append(j['password'])
        sshCon=ssh_connecter(j['ip'],j['user'],j['password'])
        sshCon.get_connect(j['retry'])
        if sshCon.conStatus == True:
            tmp=sshCon.do(cmds)
            for info in tmp:
                get.append(info)
        #for i in get:
         #   print(i)
        showResult.append(get)
    print(showResult)
    wt.csv_write_head('test')
    for p in showResult:
        wt.csv_write_body('test.csv',p)
