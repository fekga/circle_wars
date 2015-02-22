from socket import *

host,ip = '192.168.1.101', 5045

c = socket(AF_INET, SOCK_DGRAM)
c.sendto(bytes('hello','utf-8'), ('localhost',ip))