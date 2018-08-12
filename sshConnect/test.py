import paramiko
import time
import socket

ip='39.108.147.179'
username='shawn'
cmds=['who','free -h','users','exit']
password='shawn123'
s=paramiko.SSHClient()
s.load_system_host_keys()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect(hostname=ip,username=username,password=password,timeout=5)
finalOut=[]
ssh=s.invoke_shell()
out = ssh.recv(204800)
for cmd in cmds:
        time.sleep(1)
        ssh.send(cmd+'\n')
        out = ssh.recv(204800)
        finalOut.append(out)
       # print(out)
del finalOut[0]
for j in finalOut:
        if type(j) is not str:
                s = j.decode("utf-8")
        tmp = s.split('\r\n')
        j = '\r\n'.join(tmp[1:-1])

for i in finalOut:
        print(i)
ssh.close()
