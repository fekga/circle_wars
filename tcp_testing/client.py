#!/usr/bin/python           # This is client.py file

import socket               # Import socket module
import json

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12345                # Reserve a port for your service.

s.connect((host, port))
print json.loads(s.recv(1024))
s.close                     # Close the socket when done