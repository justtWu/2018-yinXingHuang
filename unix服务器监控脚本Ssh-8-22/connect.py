#coding=utf-8

from IO import writer,reader
from sshLogDeal import loggerForSsh
import paramiko
import threading
###################################################ssh connect##########################################################
class sshBaseConnecter(object):
    #连接基类，构造基本连接的配置信息
    def __init__(self,ip,userName,passWord):
        self.ip=ip
        self.userName=userName
        self.passWord=passWord
        self.port=22
        self.conStatus=False
class sshConnecter(sshBaseConnecter):
    '''
    建立连接，并完成一系列操作
    '''
    def __init__(self,ip,userName,passWord):
        super().__init__(ip,userName,passWord)
        self.sh=paramiko.SSHClient()

    #进行连接并处理异常
    def ssh_get_connect(self,retryList):
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
            elif  err:
                #print('连接超时无答复，'+self.ip+'主机未开或网络出现问题')#需要特别反应
                loggerForSsh.error("%s连接超时，目标主机未开或网络出现问题"%self.ip)
                return 0
        #若第一次尝试失败，进行密码重试
        if self.conStatus is False:
            for rePass in retryList:
                try:
                    self.sh.connect(self.ip, self.port, self.userName, rePass)
                    self.conStatus=True
                    #更新配置文件中的password
                    self.passWord = rePass
                    wd = reader()
                    wd.alterIp(self.ip,rePass)
                    break
                except Exception as e:
                    err2=str(e)
                    if err2 != '':
                        continue

        #若尝试完所有密码还是连接失败
        if self.conStatus is False:
            loggerForSsh.error('%s试完所有密码未能连接成功'%self.ip)


    #执行一系列命令
    def ssh_do(self,cmds):
        finalResult=[]
        for m in cmds:
            eachResult=''
            stdin, stdout, stderr = self.sh.exec_command(m)
            out = stdout.readlines()
            #屏幕输出
            for o in out:
                #print(o)
                eachResult = eachResult+o
            finalResult.append(eachResult)
        return finalResult

class myThread(threading.Thread):
    def __init__(self,ip,username,password,retry,cmds):
        threading.Thread.__init__(self)
        self.ip = ip
        self.username = username
        self.password = password
        self.retry = retry
        self.cmds = cmds
        self.result = []
        self.result.append(self.ip)
        self.result.append(self.username)

    def run(self):
        print('ok')
        sshCon=sshConnecter(self.ip,self.username,self.password)
        sshCon.ssh_get_connect(self.retry)
        self.result.append(sshCon.passWord)
        if sshCon.conStatus == True:
            #print(self.ip+':')
            tmp=sshCon.ssh_do(cmds)
            for info in tmp:
                self.result.append(info)

    def get_result(self):
        return self.result




if __name__ == '__main__':
    loggerForSsh.info("查看一次服务器信息")
    wd=reader()
    wt=writer()

    connect_info=wd.readIp()
    cmds=wd.readCmd()
    retry = wd.readRetry()

    ssh_showResult = []
    threads = []

    count = range(len(connect_info))
    # 添加线程到线程列表
    for j in connect_info:
        #print(j['ip'],j['user'],j['password'],retry)
        threads.append(myThread(j['ip'],j['user'],j['password'],retry,cmds))
    # 开启新线程
    for i in count:
        threads[i].setDaemon(True)
        threads[i].start()
    # 等待所有线程完成
    for i in count:
        threads[i].join()
    print('线程执行完毕！')
    #得到所有的结果
    for i in count:
        ssh_showResult.append(threads[i].get_result())
    wt.csv_write_head()
    for p in ssh_showResult:
        wt.csv_write_body(p)

