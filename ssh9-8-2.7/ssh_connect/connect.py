#coding=utf-8
from IO import writer,reader
from sshLogDeal import loggerForSsh
import os
import paramiko
import threading
###################################################ssh connect##########################################################
#连接基类，构造基本连接的配置信息
class sshBaseConnecter(object):
    #初始化基本信息，ip,userName,passWord,port,conStatus
    def __init__(self,ip,userName,passWord):
        self.ip=ip
        self.userName=userName
        self.passWord=passWord
        self.port=22
        self.conStatus=False

#建立连接，并完成一系列操作
class sshConnecter(sshBaseConnecter):
    #初始化基本信息
    def __init__(self,ip,userName,passWord):
        super(sshConnecter,self).__init__(ip,userName,passWord)
        self.sh=paramiko.SSHClient()

    #进行连接并处理异常，参数：重试密码集合，输出：无
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
                print(u'身份验证失败，重试密码中......')
            elif  err:
                loggerForSsh.error(u"%s连接超时，目标主机未开或网络出现问题"%self.ip)
                #若出现这样的状况直接退出
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
            loggerForSsh.error(u'%s试完所有密码未能连接成功'%self.ip)

    #执行一系列命令，参数：命令集合，输出：结果集合
    def ssh_do(self,cmds):
        finalResult=[]
        for m in cmds:
            eachResult=''
            stdin, stdout, stderr = self.sh.exec_command(m)
            if 'sudo' in m:
                stdin, stdout, stderr = self.sh.exec_command(m,get_pty=True)
                stdin.write(self.passWord + "\n")
                stdin.flush()
                stdout.flush()
            out = stdout.readlines()
            #屏幕输出
            for o in out:
                #print(o)
                eachResult = eachResult+o
            finalResult.append(eachResult)
        return finalResult

class myThread(threading.Thread):
    def __init__(self,connect_infos,retry,cmds,thread_number):
        """
        初始化过程需要输入一个数组connect_infos,数组中的每个元素是包含服务器基本信息的字典 {"ip":xxx,"user":"xxx","password":"123"}
        密码重试集retry
        指令集cmds
        线程编号thread_number
        """
        threading.Thread.__init__(self)
        self.connect_infos = connect_infos
        self.retry = retry
        self.cmds = cmds
        self.results = []
        self.thread_number = thread_number

    def run(self):
        print('---Thread %d Start---\n'%self.thread_number)
        if self.connect_infos is None:
            return
        for info in self.connect_infos:
            sshCon = sshConnecter(info['ip'],info["user"],info["password"])
            sshCon.ssh_get_connect(self.retry)
            fileds = [info['ip'],info['user'],sshCon.passWord]
            if sshCon.conStatus is True:
                tmp = sshCon.ssh_do(self.cmds)
                fileds += tmp
            self.results.append(fileds)

    def get_result(self):
        return self.results

def distribute(server_sum,thread_sum):
    """
    输入:server_sum:服务器的数量
         thread_sum:线程的数量
    输出:
    功能:为每个线程平均分配服务器
    """
    distribution = []
    avg = server_sum/thread_sum
    if avg == 0:
        #当线程数量比服务器总数要多的时候，多余的线程的得到的是None
        for i in range(server_sum):
            distribution.append(range(i,i+1))
        for i in range(thread_sum-server_sum):
            distribution.append(None)
    else:
        #当线程数量比服务器总数要少的时候，按平均分配的原则，有余数的时候，最后一个线程负责余数部分
        for i in range(thread_sum):
            if i == thread_sum - 1:
                distribution.append(range(i*avg,server_sum))
            else:
                distribution.append(range(i*avg,(i+1)*avg))
    return distribution

def run():
    THREAD_SUM = int(os.environ["THREAD_SUM"])
    wd=reader()
    wt=writer()

    connect_info=wd.readIp()
    #线程数为0的情况,默认改成1,但是config文件中不予改变
    if THREAD_SUM <= 0:
        loggerForSsh.warn(u"配置文件(config.py)中线程数(THREAD_SUM)应当大于0,否则执行时默认为1")
        THREAD_SUM = 1
    distribution = distribute(len(connect_info), THREAD_SUM)

    cmds=wd.readCmd()
    retry = wd.readRetry()
    ssh_showResult = []
    threads = []

    # 添加线程到线程列表
    for thread in range(THREAD_SUM):
        if distribution[thread] is None:
            #当出现None时，说明线程数量比服务器数量多，多余的线程可以开启
            break
        servers = [connect_info[i] for i in distribution[thread]]
        threads.append(myThread(servers,retry,cmds,thread))

    # 开启新线程
    thread_sum = range(len(threads))
    for thread in thread_sum:
        threads[thread].setDaemon(True)
        threads[thread].start()
    
    # 等待所有线程完成
    for thread in thread_sum:
        threads[thread].join()
    loggerForSsh.info(u"所有的线程执行完毕")
    
    #得到所有的结果
    for thread in thread_sum:
        ssh_showResult += threads[thread].get_result()

    try:
        wt.csv_write_head()
        for p in ssh_showResult:
            wt.csv_write_body(p)
    except IOError as e:
        loggerForSsh.error(u"操作csv文件失败")