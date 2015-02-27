import socket

import __builtin__
__builtin__.isserver = False

import ability

class Client(object):
	
	def __init__(self, host='localhost', port=8888):
		self.host = host
		self.port = port
		
	def __del__(self):
		self.socket.close()
		 
	def run(self):
		try:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		except socket.error, msg:
			print 'Failed to create socket, Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
			return
 
		while(1):
			msg = raw_input('Enter message to send : ')
     
			try :
				#Set the whole string
				self.socket.sendto(msg, (self.host, self.port))
				 
				d = self.socket.recvfrom(1024)
				reply = d[0]
				addr = d[1]
				 
				print 'Server reply : ' + reply
			except socket.error, msg:
				print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
				continue
	
if __name__ == '__main__':
	client = Client()
	client.run()
	ability.PassiveAbility('test_ability').use()
