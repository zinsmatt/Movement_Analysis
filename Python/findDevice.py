import bluetooth

target_name = "Losc_phone"
target_address = None



"""
nearby_devices = bluetooth.discover_devices()

for addr in nearby_devices:
	print "found address : ",addr
	if target_name == bluetooth.lookup_name(addr):
		target_address = addr
		break

if target_address is not None:
	print "found target bluetooth device " + target_name + " with address " + target_address
else:
	print "could not find target " + target_name"""



server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

port = 1
server_socket.bind(("",port))
server_socket.listen(1)

print "server listening on port " + str(port) + " ..."
client_socket, address = server_socket.accept()
print "Accepted connection from ",address

data = client_socket.recv(1024)
print "received [%s]" % data

client_socket.close()
server_socket.close()
