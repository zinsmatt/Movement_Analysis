import time
import struct
from bluetooth import *



def test_communication_time(socket, nb_max):
	values = []
	socket.send(chr(nb_max))
	socket.recv(1)
	for i in range(nb_max):
		t1 = time.time() * 1000;
		socket.send(chr(2))
		socket.recv(1)
		t2 = time.time() * 1000;
		print i,(t2-t1)/2
		values.append((t2-t1)/2)	
		time.sleep(0.5)
	#print values
	moy = sum(values)/len(values)
	print "Temps moyen = ",moy



server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
uuid = "e8e10f95-1a70-4b27-9ccf-02010264e9c8"

advertise_service( server_sock, "SampleServer",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ])

print("Waiting for connection on RFCOMM channel %d" % port)

client_sock, client_info = server_sock.accept()

print("Accepted connection from ", client_info)


while 1:

	i = int(raw_input())
	print i

	if i>1:
		test_communication_time(client_sock,i)
	else:

		str_values = [];

		client_sock.send(chr(1))
		data ="";
		data_str = ""
		print "Waiting for data ..."
		client_sock.setblocking(1)
		nb_buffer = client_sock.recv(4)
		if len(nb_buffer)!=4:
			print "Error reading nb values transmitted"
			exit()
		nb = struct.unpack('i',nb_buffer)[0]
		print nb

		while len(str_values)<nb*4:
			buf = client_sock.recv(nb*4)
			#print(str(len(buf))+" octets lus")
			#print(str(len(str_values))+" size str_vales")
			str_values += buf

		for i in range(nb):
			f_str = str(str_values[i*4])+str(str_values[i*4+1])+str(str_values[i*4+2])+str(str_values[i*4+3]);
			val = struct.unpack('f',f_str);
			print val 
			





##this part will try to get something form the client
## you are missing this part - please see it's an endlees loop!!
#try:
#    while True:
#        data = client_sock.recv(1024)
#        if len(data) == 0: break
#        print("received [%s]" % data)
#
## raise an exception if there was any error
#except IOError:
#    pass
#
#print("disconnected")

client_sock.close()
server_sock.close()