import time
import struct
from bluetooth import *


# <10 => nb sec d'enregistrement
# 10 => reponse directe pour mesurer le temp
# >10 => nb sec de synchro

def test_communication_time(socket, nb_max):
	values = []
	socket.send(chr(nb_max))
	socket.recv(1)
	for i in range(nb_max):
		t1 = time.time() * 1000;
		socket.send(chr(10))
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

	if i>=10:
		test_communication_time(client_sock,i)
	else:

		s = [];

		client_sock.send(chr(i))
		data ="";
		data_str = ""
		print("Waiting for data ...")
		client_sock.setblocking(1)
		nb_buffer = client_sock.recv(4)
		if len(nb_buffer)!=4:
			print("Error reading nb values transmitted")
			exit()
		nb = struct.unpack('i',nb_buffer)[0]
		print nb

		sizeLine = 8+3*4

		while len(s)<nb*sizeLine:		# 1 long + 3 float
			buf = client_sock.recv(nb*sizeLine)
			#print(str(len(buf))+" octets lus")
			#print(str(len(str_values))+" size str_vales")
			s += buf


		f = open('data.dat', 'w')

		for i in range(nb):
			long_str = str(s[i*sizeLine])+str(s[i*sizeLine+1])+str(s[i*sizeLine+2])+str(s[i*sizeLine+3])+str(s[i*sizeLine+4])+str(s[i*sizeLine+5])+str(s[i*sizeLine+6])+str(s[i*sizeLine+7])
			time = struct.unpack('q',long_str)[0]
			x_str = str(s[8+i*sizeLine])+str(s[8+i*sizeLine+1])+str(s[8+i*sizeLine+2])+str(s[8+i*sizeLine+3])
			y_str = str(s[12+i*sizeLine])+str(s[12+i*sizeLine+1])+str(s[12+i*sizeLine+2])+str(s[12+i*sizeLine+3])
			z_str = str(s[16+i*sizeLine])+str(s[16+i*sizeLine+1])+str(s[16+i*sizeLine+2])+str(s[16+i*sizeLine+3])
			x = struct.unpack('f',x_str)[0]
			y = struct.unpack('f',y_str)[0]
			z = struct.unpack('f',z_str)[0]
			line = str(time)+" "+str(x)+" "+str(y)+" "+str(z)+"\n"
			f.write(line)
			print line
			
		f.close()







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