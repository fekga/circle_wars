import socket

import __builtin__
__builtin__.isserver = True

import ability

class Server(object):
	
	def __init__(self, host='', port=8888):
		self.host = host
		self.port = port
		
	def __del__(self):
		self.socket.close()
		 
	def run(self):
		try:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			print 'Socket created'
		except socket.error, msg :
			print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
			return
		
		try:
			self.socket.bind((self.host, self.port))
		except socket.error, msg:
			print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
			return
			 
		print 'Socket bind complete'
		 
		while 1:
			d = self.socket.recvfrom(1024)
			data = d[0]
			addr = d[1]
			 
			if not data: 
				break
			 
			reply = 'OK...' + data
			 
			self.socket.sendto(reply , addr)
			print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
			 
	
if __name__ == '__main__':
	server = Server()
	server.run()
	ability.ToggleAbility('test_ability').use()
	ability.ToggleAbility('test_ability').use()
	ability.ToggleAbility('test_ability').use()
	ability.ToggleAbility('test_ability').use()
	ability.ToggleAbility('test_ability').use()

