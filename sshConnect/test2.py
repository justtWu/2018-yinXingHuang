import paramiko
import time

def sftp_exec_command(commands):


        instruct="ls -l".encode("ascii")
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conStatus=False
        ssh_client.connect('39.108.147.179', 22, 'shawn','shawn123')


        buf=ssh_client.invoke_shell()
        buf.send(commands+'\n')
        print(buf.recv(1024))
        #buf=ssh_client.recv(204800)
       # print(buf)

       # std_in, std_out, std_err = ssh_client.exec_command(command,get_pty=True)

        #conStatus=True
        #print(conStatus)





if __name__ == '__main__':
    sftp_exec_command("lsb_release -a")

   # sftp_exec_command("ifconfig")
 ''' #执行命令并返回结果
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
        self.sh.close()'''

   '''for j in connect_info:
        #print(j)
        sshCon=ssh_connecter(j['ip'],j['user'],j['password'])
        sshCon.get_connect(j['retry'])
        get=sshCon.exec_command("lsb_release -a;echo 'done';who | grep '([1-9]' | awk \'{print $NF}\';\\n;users;lscpu |grep \'Socket\' |awk \'{print $NF}\';free -h;exit")
        sshCon.logOut()
        for i in get:
             print(i)'''
