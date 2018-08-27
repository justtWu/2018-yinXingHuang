#coding=utf-8
import config
import csv
from sshLogDeal import loggerForSsh

#把获取到的信息写入表格的类
class writer(object):
    # 初始化需要编辑的文件:表格文件，命令信息文件（包括表格的列名信息）
    def __init__(self):
        self.result_file = config.RESULT_FILE
        self.cmd_file =  config.CMD_FILE
    # 写入CSV文件的列名，参数：无，输出：无
    def csv_write_head(self):
        finalGet = []
        flag = 0#用于只读取文件的第一行
        for line in open(self.cmd_file,encoding='UTF-8'):
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

	#写入表格内容，参数：result：获得的结果列表，输出：无
    def csv_write_body(self,result):
        with open(self.result_file, "a+", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(result)


# 读取命令信息，服务器信息，重试密码集以及重试密码成功后更正服务器正确密码的读取类
class reader(object):
     # 初始化需要用到的文件:服务器信息文件，命令信息文件，重试密码文件
    def __init__(self):
        self.ip_file = config.IP_FILE
        self.cmd_file =  config.CMD_FILE
        self.retry_file = config.RETRY_FILE

    #读取命令，参数：无，输出：命令集合
    def readCmd(self):
        cmds = []
        flag = 0#用于读文件的第二行及后面
        #需要加一个encoding='UTF-8'，因为该文件中含有中文
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

    #读取服务器信息，参数：无，输出：服务器信息集合
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

    #读取重试密码集，参数：无，输出：重试密码集合
    def readRetry(self):
        retry = []
        for line in open(self.retry_file):
            line = line.strip('\n')
            tmp = line.split(',')
            for i in tmp:
                tmp2 = i.strip()
                retry.append(tmp2.strip('"'))
        return retry

    #更改服务器的正确密码，参数：ip：对应服务器的ip，password：正确的密码 输出：无
    def alterIp(self,ip,password):
        f = open(self.ip_file,"r+")
        lines = f.readlines()
        f.close()
        with open(self.ip_file,"w") as f_w:
            for line in lines:
                if ip in line:
                    oldPassword = line.split()[2]
                    newPassword = '\"%s\"' % password
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

