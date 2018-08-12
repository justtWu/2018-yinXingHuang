#-*- coding: utf-8 -*-
#!/usr/bin/python
import paramiko
import threading
 
def ssh2(ip,username,passwd,cmd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,22,username,passwd,timeout=5)
        for m in cmd:
            stdin, stdout, stderr = ssh.exec_command(m)
#           stdin.write("Y")   #简单交互，输入 ‘Y’
            out = stdout.readlines()
            #屏幕输出
            for o in out:
                print (o)
        print ('%s\tOK\n'%(ip))
        ssh.close()
    except :
        print ('%s\tError\n'%(ip))
 
 
if __name__=='__main__':
    cmd = ['cal','echo hello!']#你要执行的命令列表
    username = "wuyuhang"  #用户名
    passwd = "1209"    #密码
    threads = []   #多线程
    print ("Begin......")
#    for i in range(1,254):
    ip = '192.168.134.130'
    a=threading.Thread(target=ssh2,args=(ip,username,passwd,cmd))
    b=threading.Thread(target=ssh2,args=("39.108.147.179","shawn","shawn123",cmd))
    a.start()
    b.start()
    threads.append(a)
    threads.append(b)
    for i in threads:
        i.join()
    
