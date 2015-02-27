'''
from socket import *

host,ip = '192.168.1.101', 5045

c = socket(AF_INET, SOCK_DGRAM)
c.sendto(bytes('hello','utf-8'), ('localhost',ip))
'''

'''
    Simple udp socket server
    Silver Moon (m00n.silv3r@gmail.com)
'''
 
import socket
import sys
 
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port
 
# Datagram (udp) socket
try :
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print 'Socket created'
except socket.error, msg :
    print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
 
 
# Bind socket to local host and port
with s.bind((HOST, PORT)) as (err,msg):
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Socket bind complete'
 
#now keep talking with the client
while 1:
    # receive data from client (data, addr)
    d = s.recvfrom(1024)
    data = d[0]
    addr = d[1]
     
    if not data: 
        break
     
    reply = 'OK...' + data
     
    s.sendto(reply , addr)
    print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
     
s.close()


 
#~ # create dgram udp socket
#~ try:
    #~ s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#~ except socket.error:
    #~ print 'Failed to create socket'
    #~ sys.exit()
 #~ 
#~ host = 'localhost';
#~ port = 8888;
 #~ 
#~ while(1) :
    #~ msg = raw_input('Enter message to send : ')
     #~ 
    #~ try :
        #~ #Set the whole string
        #~ s.sendto(msg, (host, port))
         #~ 
        #~ # receive data from client (data, addr)
        #~ d = s.recvfrom(1024)
        #~ reply = d[0]
        #~ addr = d[1]
         #~ 
        #~ print 'Server reply : ' + reply
     #~ 
    #~ except socket.error, msg:
        #~ print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        #~ sys.exit()
