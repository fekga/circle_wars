#!/usr/bin/python           # This is server.py file

import socket               # Import socket module
import json

class Server(object):

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	host = socket.gethostname()
	port = 12345
	max_listeners = 2

	msg = json.dumps({"c": 0.1e19, "b": 0, "a": 0}, sort_keys=True)

	def __init__(self):
		self.sock.bind((self.host,self.port))

	def run(self):
		self.open = True
		self.counter = 0
		self.sock.listen(self.max_listeners)
		while self.open:
			c,addr = self.sock.accept()
			print addr
			#c.send('hi!')
			c.send(self.msg)
			c.close()
			self.counter += 1
			if self.counter == self.max_listeners:
				self.open = False
		self.sock.shutdown()

server = Server()
server.run()