#coding=utf-8
import time
import telnetlib
from constants import WINDOWS_LINE_SPLITER,LINUX_LINE_SPLITER,LINE_SPLITER
from IO import writer,reader
from sshLogDeal import loggerForSsh
from telnetLogDeal import loggerForTelnet
import paramiko

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
            elif '[WinError 10060]' in err:
                #print('连接超时无答复，'+self.ip+'主机未开或网络出现问题')#需要特别反应
                loggerForSsh.error("%s连接超时，目标主机未开或网络出现问题"%self.ip)

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
                print(o)
                eachResult = eachResult+o
            finalResult.append(eachResult)
        return finalResult

#############################################telnet connect#############################################################
class telnetBaseConnecter(object):
    def __init__(self,ip,username,password,port,timeout):
        self.port = port
        self.ip = ip
        self.timeout = timeout
        self.conn = None
        self.username = username
        self.password = password
        self.con_status = False


class telnetConnecter(telnetBaseConnecter):
    def __init__(self,ip=None,username=None,password=None,port=23,timeout=50):
        super().__init__(ip,username,password,port,timeout)
        try:
            self.tn = telnetlib.Telnet(ip) #if ip is not None else None
        except:
            loggerForTelnet.error('%s连接超时，目标主机未开或网络出现问题'%self.ip)
            return None

    def telnet_connect(self,password):
        self.tn.read_until(b'login:')
        self.tn.write(self.username.encode('ascii') + WINDOWS_LINE_SPLITER)
        self.tn.read_until(b"assword:")
        self.tn.write(self.password.encode('ascii') + WINDOWS_LINE_SPLITER)
        time.sleep(5)      #休眠，因为服务器的返回内容有可能会延迟到达缓冲区，否则下一步读取会出错

    def telnet_server(ip, username, password, self=None):
        """
        输入：ip,username,password
        输出：None
        功能：重新配置需要连接的服务器的信息
        ps：意识到如果每次连接一个新服务器都构建一个新的对象，当服务器的数量特别多的时候，内存会被浪费。故而每次都利用这一个对象即可。我是代码写完之后才意识到这个问题，重构会浪费很多时间，添加这个方法可以很好地解决问题。
        TODO：解决这个不足
        """
        self.ip = ip
        self.username = username
        self.password = password
        self.tn = telnetlib.Telnet(ip)

    def telnet_get_connect(self,password_check=False,retry=[]):
        """
        输入：retry：重试密码集合，默认为空; password_check:是否提供密码校正功能，即将密码集合中的正确密码更正在json文件中
        输出：0:连接成功，1:连接失败
        功能：与服务器进行连接
        """
        try:
            self.telnet_connect(self.password)    #利用用户提供的密码进行第一次连接尝试
            check = self.password
            self.con_status=True
        except Exception as e:
            err=str(e)
            if e:
                print('%s身份验证失败，重试密码中......' % self.ip)

        if self.con_status == False:
            for i in retry:
                login_tip = self.tn.read_very_eager()
                if b"incorrect" in login_tip or login_tip is None:
                    check = i
                    self.tn.write(self.username.encode('ascii') + WINDOWS_LINE_SPLITER)
                    self.tn.read_until(b"assword:")
                    self.tn.write(i.encode('ascii') + WINDOWS_LINE_SPLITER)
                    time.sleep(5)      #休眠，因为服务器的返回内容有可能会延迟到达缓冲区，否则下一步读取会出错
                else:
                    if password_check is True:
                            wt=writer()
                            wt.updete_json(ip=self.ip,password=check,passAlter=True)
                    self.con_status = True
                    return 0

            login_tip = self.tn.read_very_eager()
            if b"login" in login_tip or login_tip is None:
                loggerForTelnet.error('%s试完所有密码未能连接成功'%self.ip)
                return 1
            else:
                if password_check is True:
                    wt=writer()
                    wt.updete_json(ip=self.ip,password=check,passAlter=True)
                self.con_status = True
                return 0

    def telnet_write(self,instruct):
        """
        输入：指令
        输出：指令得到的结果
        功能：执行指令并得到结果
        """
        time.sleep(6)
        self.tn.read_very_eager()
        if self.con_status is False:
            loggerForTelnet.error("Connection is not established. IP:%s"%self.ip)
        sock = self.telnet_get_sock()
        sock.sendall(instruct+WINDOWS_LINE_SPLITER)
        time.sleep(3)
        buf = sock.recv(204800)
        return buf

    def telnet_close(self):
        """
        输入：pass
        输出：pass
        功能:断开连接
        """
        sock = self.telnet_get_sock()
        sock.close()
        self.con_status = False

    def telnet_parse_result(self,string):
        if type(string) is not str:
            s = string.decode("utf-8")
        tmp = s.split(LINE_SPLITER)
        s = LINE_SPLITER.join(tmp[1:-1])
        return s

    def telnet_do(self,instructs):
        """
        输入：指令列表
        输出：指令执行结果列表(list)
        功能：逐条执行指令并得到结果
        """
        for i in range(len(instructs)):
            if type(instructs[i]) is not bytes:
                instructs[i] = instructs[i].encode("ascii")

        result_list = []
        for i in instructs:
            s = self.telnet_write(i)
            result = self.telnet_parse_result(s)
            result_list.append(result)
        self.telnet_close()
        return result_list

    def telnet_get_sock(self):
        return self.tn.get_socket()


if __name__ == '__main__':
    loggerForTelnet.info("查看一次服务器信息")
    loggerForSsh.info("查看一次服务器信息")
    wd=reader()
    wt=writer()
    connect_info=wd.reader_connect()
    cmds=['lsb_release -a','who | grep \'([1-9]\' | awk \'{print $NF}\'','lscpu |grep \'Socket\' |awk \'{print $NF}\'','free -h']
    ssh_showResult = []
    telnet_showResult=[]

########execute ssh_connect###########
    for j in connect_info:
        get = []
        get.append(j['ip'])
        get.append(j['user'])
        get.append(j['password'])
        sshCon=sshConnecter(j['ip'],j['user'],j['password'])
        sshCon.ssh_get_connect(j['retry'])
        if sshCon.conStatus == True:
            print(j['ip']+':')
            tmp=sshCon.ssh_do(cmds)
            for info in tmp:
                get.append(info)
        ssh_showResult.append(get)
    wt.csv_write_head('ssh_result')
    for p in ssh_showResult:
        wt.csv_write_body('ssh_result.csv',p)

########execute telnet_connect###########
    for q in connect_info:
        get = []
        get.append(q['ip'])
        get.append(q['user'])
        get.append(q['password'])
        try:
            telnetCon = telnetConnecter(q['ip'], q['user'], q['password'])
            telnetCon.telnet_get_connect(password_check=True,retry=q['retry'])
            if telnetCon.con_status == True:
                tmp=telnetCon.telnet_do(cmds)
                for info in tmp:
                    #print(info)
                    get.append(info)
            telnet_showResult.append(get)
        except:
            telnet_showResult.append(get)
            continue
    wt.csv_write_head('telnet_result')
    for p in telnet_showResult:
        wt.csv_write_body('telnet_result.csv',p)


