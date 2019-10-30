#!/usr/bin/python3
# PyProx! Simple network proxy to analyse what is passing between you and your target.





'''
pgrep -f youAppFile.py | xargs kill -9

##**pgrep return the PID of the specific file and you kill only the specific application.

pkill -9 python

##**kill all python

'''


show_mesg = [
"=20191030= VA.1 Dis/Enable MQTT by .-.-. or none ",
"=20190917= V8.3 MQTT, #brkp-002-1 PyProxRemote::,self.transport.close() ",
"=20190917= V8.2 MQTT, #brkp-001-1 PyProxLocal::,self.transport.close() ",
"=20190916= V8.1 MQTT, roll-back ; add minimal hex log type h;print_tomtqq type h , w, a,e",
"=20190915= V8 MQTT, add mqtt.;comment ##8# . ",
"=20190708= V6 Pro, Fix [*] Received--TRANS 166 bytes from local ; socket.send() raised exception. ",
"=20190624= V5 Pro, TRANS the receiver ",
"=20181211= V4 NT, improve mis-match protocol ",
"=20181209= V4 NT, fix bug trans ",
"=20181207= V4 NT, add fifo2ms ",
"=20181205= V4, add -t trans ",
"***^^ What's new *****",
]


import fifo2mt as p0
import sys
import asyncio
import socket
#import fcntl
import struct
import argparse
import datetime
import paho.mqtt.client as mqtt
#import paho_mqtt_140_client as mqtt

Verbose 	= False
Output		= 'canon'
Trans 	= False


class PyProxLocal(asyncio.Protocol):
	LocalBuffer = b""
	
	def __init__(self, remote):
		self.remote = remote
		self.remote_up = False
		
	def data_manip(self, data):
		# Manipulate data when it leaves
		return data

	def connection_made(self, transport):
		self.peername = transport.get_extra_info('peername')
		log("a", "New connection from local - {}".format(self.peername))
		transport.pause_reading()
		self.transport = transport
		asyncio.ensure_future(self.proxy_out_connect()).add_done_callback(self.remote_ready)
	
	def remote_ready(self, *args):
		self.remote_up = True
		if len(self.LocalBuffer) > 0:
			self.transport_remote.write(self.LocalBuffer)
			LocalBuffer = b""

	def connection_lost(self, ex):
		log("w", "Connection lost from local - {}".format(self.peername))
		self.transport.close()

	def data_received(self, data):
		global LocalBuffer
		print()
		##8#log("i", "Received {} bytes from local".format(len(data)))
		##8#log('i', "Timestamp: {} ".format(datetime.datetime.now()))
		##8#log("i", "Received--RAW")
		log("i", "Received {} bytes from local\r\nTimestamp: {} \r\nReceived--RAW".format(len(data), datetime.datetime.now())) ##8#
		hexdump(data, '>')
		
		if Trans:
			##8#log("i", "Received--TRANS--local")
			#dataret0 = p0.fifo2mt(data.decode('utf8'),_verbose=True)
			dataret0 = p0.fifo2mt(data.decode('utf8'),_verbose=False)
			##8#log("i", "dataret0 =  {}".format(dataret0))
			if len(dataret0)<7:
				log("i", "Error protocol convertor, Auto roll-back")
			else:
				data = dataret0.encode()

			log("i", "Received--TRANS {} bytes from local".format(len(data)))

			hexdump(data, '>')

		try:
			print("#brkp-001-00 PyProxLocal::,data=self.data_manip(data)")
			data=self.data_manip(data)
		except:
			print("#brkp-001-11 PyProxLocal::,data=self.data_manip(data)") ##8/3#

		if not self.remote_up:
			print("#brkp-001-10 PyProxLocal::,if not self.remote_up:")
			self.LocalBuffer+=data
		else:
			##8#log("i","#brkp-001-1 PyProxLocal::,self.transport_remote.write(data)")
			print("#brkp-001-1 PyProxLocal::,self.transport_remote.write(data)") ##8#
			try:
				self.transport_remote.write(data)
			except:
				##8/3#log("i","#brkp-001-1 PyProxLocal::,self.transport.close()")
				print("#brkp-001-1 PyProxLocal::,self.transport.close()") ##8/3#
				self.transport.close()

	async def proxy_out_connect(self):
		loop = asyncio.get_event_loop()
		self.transport_remote, proxy_remote = await loop.create_connection(PyProxRemote, self.remote[0], self.remote[1])
		proxy_remote.transport_local = self.transport


class PyProxRemote(asyncio.Protocol):
	
	def data_manip(self, data):
		# Manipulate data when it arrives
		return data

	def connection_made(self, transport):
		self.peername = transport.get_extra_info('peername')
		log("a", "Connection made to remote {}".format(self.peername))
		self.transport = transport

	def connection_lost(self, ex):
		log("w", "Connection lost to remote {}".format(self.peername))
		self.transport.close()

	def data_received(self, data):
		global RemoteBuffer
		print()
		##8#log("i", "Received {} bytes from remote".format(len(data)))
		##8#log('i', "Timestamp: {} ".format(datetime.datetime.now()))
		log("i", "Received {} bytes from remote\r\nTimestamp: {} ".format(len(data),datetime.datetime.now())) ##8#
		hexdump(data, '<')

		if Trans:
			##8#log("i", "Received--TRANS--remote")
			#dataret0 = p0.mt2fi(data.decode('utf8'),_verbose=True)
			dataret0 = p0.mt2fi(data.decode('utf8'),_verbose=False)
			##8#log("i", "dataret0 =  {}".format(dataret0))
			if len(dataret0)<7:
				log("i", "Error protocol convertor, Auto roll-back")
			else:
				data = dataret0.encode()

			log("i", "Received--TRANS {} bytes from remote".format(len(data)))
			hexdump(data, '<')
		
		try:
			print("#brkp-002-00 PyProxRemote::,data=self.data_manip(data)")
			data=self.data_manip(data)
		except:
			print("#brkp-002-11 PyProxRemote::,data=self.data_manip(data)") ##8/3#

		try:
			##8#log("i","#brkp-002 PyProxRemote::,self.transport_local.write(data)")
			print("#brkp-002-01 PyProxRemote::,self.transport_local.write(data)")
			self.transport_local.write(data)
		except:
			##8/3#log("i","#brkp-001-1 PyProxRemote::,self.transport.close()")
			print("#brkp-002-02 PyProxLocal::,self.transport.close()") ##8/3#
			self.transport.close()

	
def parse_params():
	parser = argparse.ArgumentParser()
	parser.add_argument('LPort', help="Local port to bind", type=int)
	parser.add_argument('RHost', help="Remote host to connect", type=str)
	parser.add_argument('RPort', help="Remote port to connect", type=int)
	parser.add_argument('-I', '--interface', help="Interface to bind to (default: lo)", required=False, default="lo")
	parser.add_argument('-M', '--mqtt', help="mqtt ip address", required=False, type=str, default="none")
	parser.add_argument('-o', '--output', help="Output type (Hexadecimal, Ascii, Canonical)", choices=['hex', 'ascii', 'canon'], required=False, default='canon')
	parser.add_argument('-v', '--verbose', help="Verbose mode", action="store_true", required=False)
	parser.add_argument('-t', '--trans', help="Transformation fifo2mt mode", action="store_true", required=False)
	return parser.parse_args()


def on_connect2(client, userdata, flags, rc):
	print('CONNACK received with code %d.' % (rc))
	#self.subscribe(MQTT_TOPIC1)
	
MQTT_TOPIC_UP = "test99/pyprox.fifo2mt/40063.up"

isconnect_mqtt_first = False
MQTTHost = ''

def log(mode, msg):
	global isconnect_mqtt_first
	global MQTTHost
	global client2
	
	mymsg = ''
	isprint_tomtqq = False

	if not MQTTHost.count('.')>=3:
		print("@Disable MQTT by default")
	else:
		if not isconnect_mqtt_first:
			isconnect_mqtt_first = True
			client2 = mqtt.Client(client_id='', clean_session=True, userdata=None, protocol=mqtt.MQTTv31)
			client2.on_connect = on_connect2
			client2.disconnect()
			client2.connect(MQTTHost, 1883)
			client2.loop_start()
			print('Connected mqtt client2')
			try:
				client2.publish(MQTT_TOPIC_UP,"MQTT Log -->Hi all,",qos=0, retain=False)
			except:
				print("MQTT Client2 PUB: Something went wrong")

	output=sys.stdout
	if Verbose:
		if mode == 'i': # Info
			output.write("[\033[32m*\033[0m] ")
			mymsg = "[\033[32m*\033[0m] "
		if mode == 'a': # Action
			output.write("[\033[33m+\033[0m] ")
			mymsg = "[\033[33m+\033[0m] "
			isprint_tomtqq = True
		if mode == 'w': # Warning
			output.write("[\033[34m!\033[0m] ")
			mymsg = "[\033[34m!\033[0m] "
			isprint_tomtqq = True
		if mode == 'h': # Hex log
			output.write("[\033[35m#\033[0m] ")
			mymsg = "[\033[35m#\033[0m] "
			isprint_tomtqq = True
	elif mode == 'e':
		output=sys.stderr
		output.write("[\033[31mx\033[0m] ")
		mymsg = "[\033[31mx\033[0m] "
		isprint_tomtqq = True
	else:
		return
	output.write(str(msg) + "\n")
	output.flush()
	
	if isconnect_mqtt_first:
		if isprint_tomtqq:
			isprint_tomtqq = False
			mymsg = mymsg + str(msg) # or no str() made died msg
			try:
				client2.publish(MQTT_TOPIC_UP,mymsg,qos=0, retain=False)
			except:
				print("MQTT Client2 PUB: Something went wrong")


def hexdump(src, origin, length=16):
	global Output
	result = []
	digits = 2

	if origin == '<':
		origin='\033[33m<'
	elif origin == '>':
		origin='\033[32m>'
	else:
		raise ValueError("Bad origin")
	
	if Output == 'ascii':
		length*=4

	for i in range(0, len(src), length):
		s = bytes(src[i:i+length])

		hexa = ' '.join(["%0*x" % (digits, x) for x in s])
		if len(hexa) < length*digits+(length-1):
			hexa= hexa + (" " * (length*digits+(length-1) - len(hexa)))

		text = ''.join(["%s" % chr(x) if 0x20 <= x < 0x7F else '.' for x in s])
		if len(text) < length:
			text = text + (" " *(length - len(text)))

		if Output == 'canon':
			result.append("%s %08x  %-*s  |%s|" % (origin, i, int(length/2), hexa, text))
		elif Output == 'hex':
			result.append("%s %08x  %-*s" % (origin, i, length, hexa))
		elif Output == 'ascii':
			result.append("%s |%s|" % (origin, text))
		else:
			raise ValueError("Wrong output")
			
	print('\n'.join(result) + '\033[0m')
	##8#log("i", "HEX: \r\n" + str(result) )
	log("h", "\r\nASCII: " + origin + str(len(src)) + "\r\n" + str(src) )
	

def if2ip(ifname):
	if ifname.count('.')>=3:
		print('@overide Interface IPv4 by xxx.x.x.x')
		ip = ifname
	else:
		import fcntl
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		ip=socket.inet_ntoa(fcntl.ioctl(
			s.fileno(),
			0x8915,
			struct.pack('256s', bytes(ifname[:15], 'utf-8'))
			)[20:24])
		s.close()

	return ip


def main():
	global Verbose, Output, Trans, MQTTHost

	for (i, val) in enumerate(show_mesg):
		print(val)


	loop = asyncio.get_event_loop()

	args = parse_params()
	if args.verbose:
		Verbose = True

	if args.trans:
		print("Trans = True")
		Trans = True

	MQTTHost = args.mqtt
	print("MQTT Host = " + MQTTHost)

	if not MQTTHost.count('.')>=3:
		print("@Disable MQTT by default")

	Output = args.output
	try:
		args.LHost=if2ip(args.interface)
		print("IP LHost: ",args.LHost)
		print("PORT LPort: ",args.LPort)	
	except Exception as e:
		log('e', "Invalid interface '{}'".format(args.interface))
		log('e', e)
		return

	log("i", "Starting...")

	coro = loop.create_server(lambda: PyProxLocal((args.RHost, args.RPort)), args.LHost, args.LPort)
	server = loop.run_until_complete(coro)
	try:
		loop.run_forever()
	except KeyboardInterrupt:
		pass
	except Exception as e:
		log("e", "Error during event_loop execution")
		log("e", e)
	finally:
		log("i", "Closing pyProx")
		server.close()
		loop.close()


if __name__=='__main__':
	main()
