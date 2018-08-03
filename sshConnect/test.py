import paramiko
import time

def sftp_exec_command(command):


        instruct="ls -l".encode("ascii")
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conStatus=False
        ssh_client.connect('192.168.134.130', 22, 'wuyuhang','1209')
        std_in, std_out, std_err = ssh_client.exec_command(command)
        buf=ssh_client.invoke_shell()
        #buf=ssh_client.recv(204800)
        print(buf)

       # std_in, std_out, std_err = ssh_client.exec_command(command,get_pty=True)
        #for line in std_out:
         #   print (line.strip("\n"))
        #conStatus=True
        #print(conStatus)





if __name__ == '__main__':
    sftp_exec_command("ls -l")
   # sftp_exec_command("ifconfig")
