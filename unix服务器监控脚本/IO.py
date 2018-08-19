#coding=utf-8
import config
import csv
import json
from sshLogDeal import loggerForSsh
from telnetLogDeal import loggerForTelnet

class writer(object):
    # 初始化需要编辑的文件
    def __init__(self):
        self.ip_json_file = config.IP_JSON_FILE

    #修改特定ip的正确登录密码
    def alter_pass(self,js,ip,password):
        for i in js['server']:
            if i['ip'] == ip:
                i['password'] = password
        loggerForTelnet.info("修改%s的正确密码为%s"%(ip,password))
        loggerForSsh.info("修改%s的正确密码为%s"%(ip,password))
        return json.dumps(js)

    # 增加特定ip的重试集
    def _retry_add(self, js, ip, array):
        for i in js['server']:
            if i['ip'] == ip:
                i['retry'] += array
                # print(i.retry)
        # js["retry_set"] = list(set(js["retry_set"]))
        loggerForTelnet.info("增加%s的重试密码%s"%(ip,array))
        loggerForSsh.info("增加%s的重试密码%s"%(ip,array))
        return json.dumps(js)

    # 删除特定ip的特定重试密码
    def _retry_del(self, js, ip, delt):
        for i in js['server']:
            if i['ip'] == ip:
                for j in i['retry']:
                    if j == delt:
                        i['retry'].remove(j)
        loggerForTelnet.info("删除%s的重试密码%s"%(ip,delt))
        loggerForSsh.info("删除%s的重试密码%s"%(ip,delt))
        return json.dumps(js)

    # 增加一个服务器
    def _ip_add(self, js, ip, user, password):
        tmp = {"ip": ip, "password": password, "user": user, "retry": []}
        js['server'].append(tmp)
        loggerForTelnet.info("增加服务器%s"%ip)
        loggerForSsh.info("增加服务器%s"%ip)
        return json.dumps(js)

    # 删除一个服务器
    def _ip_del(self, js, ip):
        tmp = js['server'].copy()
        for i in tmp:
            if i['ip'] == ip:
                js['server'].remove(i)
        loggerForTelnet.info("删除服务器%s"%ip)
        loggerForSsh.info("删除服务器%s"%ip)
        return json.dumps(js)

    # 写入CSV文件的列名
    def csv_write_head(self, filename):
        if not filename[-4:] == '.csv':
            filename = filename + '.csv'
        head_infos = ["IP", "登录用户名","密码","操作系统类型","其他登录用户","CPU个数","内存使用情况"]
        with open(filename, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(head_infos)

	#写入表格内容
    def csv_write_body(self,filename,result):
        with open(filename, "a+", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(result)

    # 更新的方法，选择调用函数
    def updete_json(self, ip, array=[], user=None, password=None,passAlter=False, retryAdd=False, retryDelete=False, ipAdd=False,
                    ipDelect=False, alter=False):
        with open(self.ip_json_file) as f:
            string = f.read()
        js = json.loads(string)
        # print(js)

        if retryAdd is True:
            string = self._retry_add(js, ip, array)
        elif retryDelete is True:
            for i in array:
                string = self._retry_del(js, ip, i)
        elif ipAdd is True:
            string = self._ip_add(js, ip, user, password)
        elif ipDelect is True:
            string = self._ip_del(js, ip)
        elif passAlter is True:
            string = self.alter_pass(js,ip,password)

        with open(self.ip_json_file, 'w') as f:
            f.write(string)

# 读取信息，分为【ip,user,password】,【retry】两个集合
class reader(object):
    def __init__(self):
        self.ip_json_file = config.IP_JSON_FILE

    def reader_connect(self):
        with open(self.ip_json_file) as f:
            string = f.read()
        js = json.loads(string)
        result = []
        for i in js['server']:
            result.append(i)
        return result


if __name__ == "__main__":
    wt = writer()
   # wt.updete_json(ip= "39.108.147.179",password='123',passAlter=True)
    wt.csv_write('test')
    #wd = reader()
   # p = wd.reader_connect()
   # print(p)
