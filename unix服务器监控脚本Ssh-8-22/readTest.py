def readCmd():
    cmds = []
    flag = 0
    for line in open("cmdConfig.txt",encoding='UTF-8'):
        if flag != 0:
            tmp = line.split(',')
            for i in tmp:
                cmds.append(i.strip())
        flag +=1
    return cmds

def readHead():
    get = []
    finalGet = []
    flag = 0
    for line in open("cmdConfig.txt",encoding='UTF-8'):
        if flag == 0:
            get = line.split(',')
            for i in get:
                finalGet.append(i.strip())
        flag += 1
    return finalGet

def readIp():
    connectInfo = []
    for line in open("ipConfig.txt"):
        tmp = {'ip':0,'user':0,'password':0}
        tmp['ip'] = line.split()[0].strip('"')
        tmp['user'] = line.split()[1].strip('"')
        tmp['password'] = line.split()[2].strip('"')
        #print(line.split())
        connectInfo.append(tmp)
    return connectInfo
def readRetry():
        retry = []
        for line in open('retry.txt'):
            line = line.strip('\n')
            tmp = line.split(',')
            for i in tmp:
                tmp2 = i.strip()
                retry.append(tmp2.strip('"'))
        return retry
def alterIp(ip,password):
    f = open("ipConfig.txt","r+")
    lines = f.readlines()
    f.close()
    with open("ipConfig.txt","w") as f_w:
        for line in lines:
            if ip in line:
                oldPassword = line.split()[2]
                newPassword = '\"%s\"' % password
                print(oldPassword,newPassword)
                line = line.replace(oldPassword,newPassword)
            f_w.write(line)
    f_w.close()

alterIp("192.168.134.138","1209")
