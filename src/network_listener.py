from socket import *

host,ip = '192.168.1.101', 5045

s = socket(AF_INET, SOCK_DGRAM)
s.bind(('localhost',ip)) #bind to localhost

while True:
    data,address = s.recvfrom(1024)
    print('Received:\n{}\nfrom:{}\n'.format(data,address))