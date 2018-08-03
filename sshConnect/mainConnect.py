import paramiko
from IO import reader,writer
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

    #进行连接并处理异常
    def get_connect(self,retryList):
        #允许连接不在know_hosts文件中的主机。
        self.sh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #用原始密码连接做第一次尝试
        try:
            self.sh.connect(self.ip, self.port, self.userName, self.passWord)
            self.conStatus=True
        except Exception as e:
            err=str(e)
            if 'Authentication failed' in err:
                print('身份验证失败，重试密码中......')
            elif '[WinError 10060]' in err:
                #print('连接超时无答复，'+self.ip+'主机未开或网络出现问题')#需要特别反应
                logger.error("%s连接超时，目标主机未开或网络出现问题"%self.ip)
                #exit(1)
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
            #print('%s试完所有密码未能连接成功'%self.ip)
            logger.error('%s试完所有密码未能连接成功'%self.ip)

        return self.conStatus
    #执行命令并返回结果
    def  exec_command(self,commandList):
        if self.conStatus==True:
            finalResult=[]
            commandList.encode()
            std_in, std_out, std_err = self.sh.exec_command(commandList,get_pty=True)
            for line in std_out:
                finalResult.append(line.strip('\n'))
        if finalResult is None:
            return ""
        else:
            return finalResult
    #登出
    def logOut(self):
        self.sh.close()

if __name__ == '__main__':
    logger.info("查看一次服务器信息")
    wd=reader()
    connect_info=wd.reader_connect()
    for j in connect_info:
        #print(j)
        sshCon=ssh_connecter(j['ip'],j['user'],j['password'])
        sshCon.get_connect(j['retry'])
        get=sshCon.exec_command("lsb_release -a;who | grep '([1-9]' | awk \'{print $NF}\';users;lscpu |grep \'Socket\' |awk \'{print $NF}\';free -h;exit")
        sshCon.logOut()
        for i in get:
             print(i)

