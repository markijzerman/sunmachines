
#https://github.com/ptone/pyosc

from OSC import OSCServer,OSCClient, OSCMessage
import sys, signal
from time import sleep
import types

def signal_handler(signal, frame):
    print("\nprogram exiting gracefully, shutting down server")
    server.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

server = OSCServer( ("0.0.0.0", 56000) ) 

def handle_timeout(self):
	print ("Timeout")

server.handle_timeout = types.MethodType(handle_timeout, server)

def fader_callback(path, tags, args, source):
	# print ("path", path)
    if path == '/1/fader1':
        print(args)
    if path == '/1/fader2':
        print(args)


server.addMsgHandler( "/1/fader1",fader_callback)
server.addMsgHandler( "/1/fader2",fader_callback)


while True:
	server.handle_request()




