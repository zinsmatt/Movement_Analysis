
from threading import Thread
from Tkinter import *
import os
import time
import struct
import mmap
import tkMessageBox
from bluetooth import *

nb_sec_rec = 3

class Appli(Tk):
	def __init__(self):
		Tk.__init__(self)

		self.isAndroidConnected = True
		self.isKinectConnected = False
		self.isOpen = True

		self.label_android_connected = Label(self,text="No Android connected");
		self.label_android_connected.pack()

		self.android_connection_thread = Thread(target=self.androidConnection)
		self.android_connection_thread.start()

		self.button_start_kinect = Button(self,text="Demarrer Kinect",command=self.startKinect)
		self.button_start_kinect.pack()

		self.button_start_recording = Button(self,text="Demarrer enregistrement",command=self.startRecording)
		self.button_start_recording.pack()
		self.button_start_recording.config(state="disabled")




	def androidConnection(self):
		""" connexion au smartphone dans un thread """
		server_sock=BluetoothSocket( RFCOMM )
		server_sock.bind(("",PORT_ANY))
		server_sock.listen(1)
		port = server_sock.getsockname()[1]
		uuid = "e8e10f95-1a70-4b27-9ccf-02010264e9c8"
		advertise_service( server_sock, "SampleServer",
						   service_id = uuid,
						   service_classes = [ uuid, SERIAL_PORT_CLASS ],
						   profiles = [ SERIAL_PORT_PROFILE ])
		print "Waiting for connection on RFCOMM channel %d" % port

		self.client_sock = None
		while self.isOpen and self.client_sock == None:
			try:
				server_sock.setblocking(0)
				self.client_sock, self.client_info = server_sock.accept()
			except :
				pass
		if self.isOpen:
			print "Accepted connection from ", self.client_info
			self.label_android_connected.config(text="Android "+self.client_info[0]+" connected");
			self.isAndroidConnected = True;
			if self.isKinectConnected:
				self.button_start_recording.config(state="normal")




	def startKinect(self):
		""" demarrer le prog C++ de la Kinect """
		self.prog = os.startfile("C:\Users\Matthieu\Documents\MI12\Projet_test\Kinect_test\Release\Kinect_test.exe")
		time.sleep(2)
		self.shm = mmap.mmap(0, 512, "Local\\Test") #You should "open" the memory map file instead of attempting to create it..
		if self.shm:
			#self.self.shm.write(bytes("5", 'UTF-8'));
			#self.shm.write(bytes("Hello", 'UTF-8'))
			time.sleep(0.5)
			self.shm.write_byte(chr(1))
			self.shm.seek(1)
			print "wrote 1"
			b = chr(0)
			while ord(b) == 0:
				b = self.shm.read_byte()
				self.shm.seek(1)
				print "recieved ", ord(b)
				time.sleep(0.1)
			print "Kinect programme pret pour enregistrement"
			self.isKinectConnected = True
			if self.isAndroidConnected:
				self.button_start_recording.config(state="normal")

			# init de la com
			self.shm.seek(0)
			self.shm.write_byte(chr(0))	# isTracking => 0
			self.shm.write_byte(chr(0))	# isRecording => 0

	def isKinectTracking(self):
		self.shm.seek(0)
		b = self.shm.read_byte()
		#print "bb ==== ", ord(b)
		return ord(b) == 1



	def startRecording(self):
		""" demarre l'enregistrement """
		# 1 ==> synchronisation android

		# 2 ==> demarrage
		if not self.isKinectTracking():
			tkMessageBox.showinfo("Avertissement", "La Kinect ne suit pas personne")
		else:
			print "Lancement de l'enregistrement"

			self.kinect_recording_thread = Thread(target=self.startKinectRecording)
			self.kinect_recording_thread.start()

			self.android_recording_thread = Thread(target=self.startAndroidRecording)
			self.android_recording_thread.start()

			self.kinect_recording_thread.join()
			self.android_recording_thread.join()
			print "Stop recording"

	def startKinectRecording(self):
		""" thread qui demarre l'enregistrement sur la kinect puis l'arrete """
		print "Kinect demarre l'enregistrement"
		print time.time();
		self.shm.seek(1)
		self.shm.write_byte(chr(1))
		time.sleep(nb_sec_rec)
		print "Fin Kinect enregistrement"
		self.shm.seek(1)
		self.shm.write_byte(chr(0))

	def startAndroidRecording(self):
		""" thread qui demarre l'enregistrement sur le smartphone """
		self.client_sock.send(chr(nb_sec_rec))	
		print("Waiting for data ...")
		self.client_sock.setblocking(1)
		nb_buffer = self.client_sock.recv(4)
		if len(nb_buffer)!=4:
			print("Error reading nb values transmitted")
			exit()
		nb = struct.unpack('i',nb_buffer)[0]
		print nb
		sizeLine = 8+3*4
		s=[]
		while len(s)<nb*sizeLine:		# 1 long + 3 float
			buf = self.client_sock.recv(nb*sizeLine)
			s += buf

		f = open('smartphone.dat', 'w')

		for i in range(nb):
			long_str = str(s[i*sizeLine])+str(s[i*sizeLine+1])+str(s[i*sizeLine+2])+str(s[i*sizeLine+3])+str(s[i*sizeLine+4])+str(s[i*sizeLine+5])+str(s[i*sizeLine+6])+str(s[i*sizeLine+7])
			time = struct.unpack('q',long_str)[0]
			x_str = str(s[8+i*sizeLine])+str(s[8+i*sizeLine+1])+str(s[8+i*sizeLine+2])+str(s[8+i*sizeLine+3])
			y_str = str(s[12+i*sizeLine])+str(s[12+i*sizeLine+1])+str(s[12+i*sizeLine+2])+str(s[12+i*sizeLine+3])
			z_str = str(s[16+i*sizeLine])+str(s[16+i*sizeLine+1])+str(s[16+i*sizeLine+2])+str(s[16+i*sizeLine+3])
			rot_matrix = []
			for k in range(1,10):
				val_str = str(s[16+i*sizeLine+4*k])+str(s[16+i*sizeLine+1+4*k])+str(s[16+i*sizeLine+2+4*k])+str(s[16+i*sizeLine+3+4*k])
				rot_matrix.append(struct.unpack('f',val_str)[0])
			x = struct.unpack('f',x_str)[0]
			y = struct.unpack('f',y_str)[0]
			z = struct.unpack('f',z_str)[0]
			line = str(time)+" "+str(x)+" "+str(y)+" "+str(z)+" "
			for k in range(9):
				line += str(rot_matrix[k])+" ";
			line+="\n"
			f.write(line)
			#print line
			
		f.close()
		print "Mesurer du smartphone enregistree"

	def destroy(self):
		print "LOSC"
		self.isOpen = False
		self.android_connection_thread.join()
		Tk.destroy(self)


app = Appli()
app.mainloop()