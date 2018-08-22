#coding=utf-8
import config
import csv
from sshLogDeal import loggerForSsh
from config import RESULT_FILE,IP_FILE,CMD_FILE,RETRY_FILE

class writer(object):
    # 初始化需要编辑的文件
    def __init__(self):
        self.result_file = config.RESULT_FILE

    # 写入CSV文件的列名
    def csv_write_head(self):
        finalGet = []
        flag = 0
        for line in open("cmdConfig.txt",encoding='UTF-8'):
            if flag == 0:
                get = line.split(',')
                for i in get:
                    i.strip('"')
                    finalGet.append(i.strip())
            flag += 1
        headInfo = []
        for info in finalGet:
            headInfo.append(info.strip('"'))
        #head_infos = ["IP", "登录用户名","密码","操作系统类型","其他登录用户","CPU个数","内存使用情况"]
        with open(self.result_file, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headInfo)

	#写入表格内容
    def csv_write_body(self,result):
        with open(self.result_file, "a+", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(result)


# 读取信息，分为【ip,user,password】,【retry】两个集合
class reader(object):
    def __init__(self):
        self.ip_file = config.IP_FILE
        self.cmd_file =  config.CMD_FILE
        self.retry_file = config.RETRY_FILE


    def readCmd(self):
        cmds = []
        flag = 0
        for line in open(self.cmd_file,encoding='UTF-8'):
            if flag != 0:
                tmp = line.split(',')
                for i in tmp:
                    cmds.append(i.strip())
            flag += 1
        fianlCmds = []
        for info in cmds:
            fianlCmds.append(info.strip('\''))
        return fianlCmds

    def readIp(self):
        connectInfo = []
        for line in open(self.ip_file):
            tmp = {'ip':0,'user':0,'password':0}
            tmp['ip'] = line.split()[0].strip('"')
            tmp['user'] = line.split()[1].strip('"')
            tmp['password'] = line.split()[2].strip('"')
            #print(line.split())
            connectInfo.append(tmp)
        return connectInfo

    def readRetry(self):
        retry = []
        for line in open(self.retry_file):
            line = line.strip('\n')
            tmp = line.split(',')
            for i in tmp:
                tmp2 = i.strip()
                retry.append(tmp2.strip('"'))
        return retry

    def alterIp(self,ip,password):
        f = open(self.ip_file,"r+")
        lines = f.readlines()
        f.close()
        with open(self.ip_file,"w") as f_w:
            for line in lines:
                if ip in line:
                    oldPassword = line.split()[2]
                    newPassword = '\"%s\"' % password
                    #print(oldPassword,newPassword)
                    line = line.replace(oldPassword,newPassword)
                f_w.write(line)
        f_w.close()
        loggerForSsh.info("修改%s的正确密码为%s"%(ip,password))
if __name__ == "__main__":
    wt = writer()
    wt.csv_write_head()
    wr = reader()
    p=wr.readRetry()
    print(p[0])

