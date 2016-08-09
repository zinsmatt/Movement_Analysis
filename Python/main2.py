
from threading import Thread
from Tkinter import *
import os
import time
import struct
import mmap
import tkMessageBox
from bluetooth import *
import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate
from scipy import signal
import matplotlib

def normaliser2(a,b):
	maxi = max(abs(a).max(),abs(b).max())
	return a/maxi, b/maxi

nb_sec_rec = 2

class Appli(Tk):
	def __init__(self):
		Tk.__init__(self)

		self.isAndroidConnected = True
		self.isKinectConnected = False
		self.isOpen = True

		self.label_android_connected = Label(self,text="Android non connecte");
		self.label_android_connected.pack()

		self.android_connection_thread = Thread(target=self.androidConnection)
		self.android_connection_thread.start()

		self.android_start_thread = Thread(target=self.androidWaitStart)

		self.button_start_kinect = Button(self,text="Demarrer Kinect",command=self.startKinect)
		self.button_start_kinect.pack()

		self.button_start_recording = Button(self,text="Demarrer enregistrement",command=self.startRecording)
		self.button_start_recording.pack()
		self.button_start_recording.config(state="disabled")

		self.spin_box_duree = Spinbox(self, from_=1, to=5)
		self.spin_box_duree.pack()

		self.label_log = Label(self,text="");
		self.label_log.pack()

		self.button_traitement = Button(self,text="Traitement",command=self.startTraitement)
		self.button_traitement.pack()
		#self.button_traitement.config(state="disabled")

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
			#if self.isKinectConnected:
			self.button_start_recording.config(state="normal")
			self.android_start_thread.start()




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
		print "iskinecttrackning?"
		if hasattr(self,'shm'):
			self.shm.seek(0)
			b = self.shm.read_byte()
			#print "bb ==== ", ord(b)
			print "? ",ord(b)==1
			return ord(b) == 1
		else:
			print "shm non cree"
			return False



	def startRecording(self):
		""" demarre l'enregistrement """
		self.button_traitement.config(state="disabled")
		if not self.isKinectTracking():
			print "Kinect ne track pas"
			self.label_log.config(text="La Kinect ne suit pas personne")
			self.android_start_thread = Thread(target=self.androidWaitStart)
			self.android_start_thread.start()
		else:
			print "Lancement de l'enregistrement"

			self.kinect_recording_thread = Thread(target=self.startKinectRecording)
			self.kinect_recording_thread.start()
			self.android_recording_thread = Thread(target=self.startAndroidRecording)
			self.android_recording_thread.start()

			self.kinect_recording_thread.join()
			self.android_recording_thread.join()
			print "Stop recording"

			self.android_start_thread = Thread(target=self.androidWaitStart)
			self.android_start_thread.start()
			self.button_traitement.config(state="normal")


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
		sizeLine = 8+3*4+9*4
		s=[]
		while len(s)<nb*sizeLine:		# 1 long + 3 float
			buf = self.client_sock.recv(nb*sizeLine)
			s += buf

		f = open('smartphone.txt', 'w')

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

	def androidWaitStart(self):
		print "Wait android start"
		self.client_sock.setblocking(1)
		self.client_sock.recv(4)
		print "Android demande enregistrement"
		self.startRecording()

	def startTraitement(self):
		"""self.thread_traitement = Thread(target=self.threadStartTraitement)
		self.thread_traitement.start()

	def threadStartTraitement(self):"""
		smartphone = np.loadtxt('smartphone.txt');
		left = np.loadtxt('data_hand_left.txt');
		right = np.loadtxt('data_hand_right.txt');

		print smartphone.shape
		print left.shape
		print right.shape


		# -------------- smartphone -----------------
		print "-------------- SMARTPHONE --------------"

		tsm = smartphone[:,0].copy()
		tsm = tsm-tsm[0]
		tsm2 = np.roll(tsm,1)

		"""a = tsm[1::]
		b = tsm2[1::]
		plt.grid(1)
		plt.xlabel('Echantillonnage')
		plt.ylabel("Periode d'echantillonnage (ms)")
		plt.plot(a-b,'.-r')
		plt.axis([0,a.size,0,60])
		plt.show()"""

		tsm = tsm / 1000



		mesures = np.array([smartphone[:,1].copy(),smartphone[:,2].copy(),smartphone[:,3].copy(),np.ones(tsm.size)])

		rot = []
		for i in range(tsm.size):
			mat = np.reshape(smartphone[i,4::].copy(),(3,3))
			mat = np.hstack((mat,[[0],[0],[0]]))
			mat = np.vstack((mat,[0,0,0,1]))
			rot.append(mat.copy())


		acc = np.array([])
		for i in range(tsm.size):
			temp = rot[i].dot(mesures[:,i])
			temp = temp.reshape(temp.size,1)
			#print "mesures ",mesures[:,i].shape
			#print "acc ", acc.shape
			#print "temp ", temp.shape
			acc = np.hstack((acc,temp)) if acc.size else temp.copy()

		# filtrage
		accx_filtered = signal.medfilt(acc[0,:])
		accy_filtered = signal.medfilt(acc[2,:])

		#integration
		vx = integrate.cumtrapz(accx_filtered,tsm, initial=0)
		vy = integrate.cumtrapz(accy_filtered,tsm, initial=0)

		vxn, vyn = normaliser2(vx,vy)


		# ==== aff courbes ========
		# affichage rotation
		"""
		plt.figure(1)
		plt.subplot(121)
		plt.xlabel('temps (s)')
		plt.ylabel('accelerations (m/s^2)')
		plt.title('Repere "smartphone"')
		plt.plot(tsm,mesures[0,:],'g',tsm,mesures[1,:],'b',tsm,mesures[2,:],'r')
		plt.subplot(122)
		plt.xlabel('temps (s)')
		plt.ylabel('accelerations (m/s^2)')
		plt.title('Repere "monde"')
		plt.plot(tsm,acc[0,:],'g',tsm,acc[2,:],'r')
		plt.show()

		 #affichage vy_filtered
		plt.figure(1)
		plt.subplot(121)
		plt.xlabel('temps (s)')
		plt.ylabel('accelerations (m/s^2)')
		plt.title('Mesures')
		plt.plot(tsm,acc[0,:],'g',tsm,acc[2,:],'r')
		plt.subplot(122)
		plt.xlabel('temps (s)')
		plt.ylabel('accelerations (m/s^2)')
		plt.title('Mesures filtrees')
		plt.plot(tsm,accx_filtered,'g',tsm,accy_filtered,'r')
		plt.show()



		# acc vit filt
		plt.figure(1)
		plt.subplot(131)
		plt.xlabel('temps (s)')
		plt.ylabel('accelerations (m/s^2)')
		plt.title('Mesures filtrees')
		plt.plot(tsm,accx_filtered,'g',tsm,accy_filtered,'r')
		plt.subplot(132)
		plt.xlabel('temps (s)')
		plt.ylabel('vitesses (m/s)')
		plt.title('Vitesses')
		plt.plot(tsm,vx,'g',tsm,vy,'r')
		plt.subplot(133)
		plt.xlabel('temps (s)')
		plt.ylabel('accelerations (m/s)')
		plt.title('Vitesses normalisees')
		plt.plot(tsm,vxn,'g',tsm,vyn,'r')
		#plt.show()
		"""
		# ------------------ Kinect -------------------
		print "-------------- KINECT --------------"

		left[:,2]= 480-left[:,2]
		right[:,2]= 480-right[:,2]

		# time
		tk = left[:,0].copy()
		for i in range(tk.size-2):
			if tk[i] == tk[i+1]:
				tk[i+1] = (tk[i]+tk[i+2])/2
		tk = tk-tk[0]
		tk = tk/1000

		# left hand
		vxl = np.array([0])
		vyl = np.array([0])
		vxr = np.array([0])
		vyr = np.array([0])
		for i in range(1,tk.size):
			dx = left[i,1]-left[i-1,1]
			dy = left[i,2]-left[i-1,2]
			dt = tk[i]-tk[i-1]
			vxl = np.append(vxl,dx/dt)
			vyl = np.append(vyl,dy/dt)
			dx = right[i,1]-right[i-1,1]
			dy = right[i,2]-right[i-1,2]
			vxr = np.append(vxr,dx/dt)
			vyr = np.append(vyr,dy/dt)

		# median filter
		vxlf = signal.medfilt(vxl)
		vylf = signal.medfilt(vyl)
		vxrf = signal.medfilt(vxr)
		vyrf = signal.medfilt(vyr)

		# normalisation
		vxln,vyln = normaliser2(vxlf,vylf)
		vxrn,vyrn = normaliser2(vxrf,vyrf)

		"""
		plt.figure(2)
		plt.subplot(231)
		plt.xlabel('temps (s)')
		plt.ylabel('position (pixel)')
		plt.title('Mouvement main gauche')
		plt.axis([0,600,0,520])
		plt.plot(left[:,1],left[:,2],'.b')
		plt.subplot(232)
		plt.xlabel('temps (s)')
		plt.ylabel('vitesses')
		plt.title('Vitesses main gauche')
		plt.plot(tk,vxl,'g',tk,vyl,'r')
		plt.subplot(233)
		plt.xlabel('temps (s)')
		plt.ylabel('vitesses')
		plt.title('Vitesses filtrees et normalisees (G)')
		plt.plot(tk,vxln,'g',tk,vyln,'r')

		plt.subplot(234)
		plt.xlabel('temps (s)')
		plt.ylabel('position (pixel)')
		plt.title('Mouvement main droite')
		plt.axis([0,600,0,520])
		plt.plot(right[:,1],right[:,2],'.b')
		plt.subplot(235)
		plt.xlabel('temps (s)')
		plt.ylabel('vitesses')
		plt.title('Vitesses main droite')
		plt.plot(tk,vxr,'g',tk,vyr,'r')
		plt.subplot(236)
		plt.xlabel('temps (s)')
		plt.ylabel('vitesses')
		plt.title('Vitesses filtrees et normalisees (D)')
		plt.plot(tk,vxrn,'g',tk,vyrn,'r')
		"""
		#plt.show();


		#  ------------------ comparaison -----------------
		print "-------------- COMPARAISON --------------"

		# interpolation
		tt = np.linspace(0,min(max(tk),max(tsm)),num=100)

		sm_interx = np.interp(tt,tsm,vxn)
		sm_intery = np.interp(tt,tsm,vyn)
		l_interx = np.interp(tt,tk,vxln)
		l_intery = np.interp(tt,tk,vyln)
		r_interx = np.interp(tt,tk,vxrn)
		r_intery = np.interp(tt,tk,vyrn)	

		"""plt.figure(3)
		plt.subplot(121)
		plt.xlabel('temps (s)')
		plt.ylabel('vitesses')
		plt.title('Echantillonnage initial')
		plt.grid(1)
		plt.plot(tk,vxln,'.-g',tk,vyln,'.-r')
		plt.subplot(122)
		plt.xlabel('temps (s)')
		plt.ylabel('vitesses')
		plt.title('Re-echantillonnage')
		plt.grid(1)
		plt.plot(tt,l_interx,'.-g',tt,l_intery,'.-r')
		"""
		"""
		plt.subplot(223)
		plt.xlabel('temps (s)')
		plt.ylabel('vitesses')
		plt.title('Echantillonnage initial')
		plt.grid(1)
		plt.plot(tsm,vxn,'.-g',tsm,vyn,'.-r')
		plt.subplot(224)
		plt.xlabel('temps (s)')
		plt.ylabel('vitesses')
		plt.title('Re-echantillonnage')
		plt.grid(1)
		plt.plot(tt,sm_interx,'.-g',tt,sm_intery,'.-r')"""

		plt.show()


		v_sm = np.array([sm_interx,sm_intery])
		v_left = np.array([l_interx,l_intery])
		v_right = np.array([r_interx,r_intery])

		#comparaison
		deltamax = 20
		diff_l = np.array([])
		diff_r = np.array([])
		"""
		plt.figure(4)
		plt.subplot(121)
		plt.xlabel('temps (s)')
		plt.ylabel('vitesses')
		plt.title('Initial')
		plt.plot(tt,v_right[0,:],'g',tt,v_right[1,:],'r',tt,v_sm[0,:],'--g',tt,v_sm[1,:],'--r')"""
		save_cl, save_cr, save_idx = [], [], []
		for delta in range(0,-deltamax-1,-1):
			
			idx = np.arange(tt.size+delta)
			cl = np.roll(v_left,delta)[:,idx]
			cr = np.roll(v_right,delta)[:,idx]
			csm = v_sm[:,idx]
			save_cl.append(cl)
			save_cr.append(cr)
			save_idx.append(idx)

			dl = np.sum(np.square(cl-csm),axis=1)
			dr = np.sum(np.square(cr-csm),axis=1)

			"""#plt.plot(tt[idx],cl[0,:],'b',tt[idx],cl[1,:],'g',tt[idx],csm[0,:],'r',tt[idx],csm[1,:],'r')
			plt.subplot(122)
			plt.xlabel('temps (s)')
			plt.ylabel('vitesses')
			plt.title('Decalage temporel')
			plt.plot(tt[idx],cr[0,:],'g',tt[idx],cr[1,:],'r',tt[idx],csm[0,:],'--g',tt[idx],csm[1,:],'--r')"""

			dtot_l = np.sum(np.square(dl))/idx.size
			dtot_r = np.sum(np.square(dr))/idx.size
			#print "delta l = ",delta," diff=  ",dtot_l	
			#print "delta r = ",delta," diff=  ",dtot_r	

			diff_l = np.append(diff_l,dtot_l)
			diff_r = np.append(diff_r,dtot_r)

		dist_left = np.min(diff_l)
		dist_left_idx = np.argmin(diff_l)
		dist_right = np.min(diff_r)
		dist_right_idx = np.argmin(diff_r)



		res_str = ""
		index = 0
		if dist_left<dist_right:
			dist_right = diff_r[dist_left_idx]
			index = dist_left_idx
			res_str += "- distance main gauche : " + str(dist_left) + "\n"
			res_str += "- distance main droite : " + str(dist_right) + "\n"
			res_str += "===========> main GAUCHE"

		else:
			dist_left = diff_l[dist_right_idx]
			index = dist_right_idx
			res_str += "- distance main gauche : " + str(dist_left) + "\n"
			res_str += "- distance main droite : " + str(dist_right) + "\n"
			res_str += "===========> main DROITE"


		self.label_log.config(text=res_str)
		self.label_log.update()

		plt.figure(1)
		plt.subplot(231)
		plt.xlabel('temps (s)')
		plt.ylabel('position (pixel)')
		plt.title('Mouvement main gauche')
		plt.axis([0,600,0,520])
		plt.plot(left[:,1],left[:,2],'.b')
		plt.subplot(232)
		plt.xlabel('temps (s)')
		plt.ylabel('vitesses')
		plt.title('Vitesses main gauche')
		plt.plot(tt[save_idx[index]],save_cl[index][0,:],'g',tt[save_idx[index]],save_cl[index][1,:],'r')
		plt.subplot(233)
		plt.xlabel('temps (s)')
		plt.ylabel('vitesses')
		plt.title('Vitesses telephone')
		plt.plot(tk,vxln,'g',tk,vyln,'r')

		plt.subplot(234)
		plt.xlabel('temps (s)')
		plt.ylabel('position (pixel)')
		plt.title('Mouvement main gauche')
		plt.axis([0,600,0,520])
		plt.plot(right[:,1],right[:,2],'.b')
		plt.subplot(235)
		plt.xlabel('temps (s)')
		plt.ylabel('vitesses')
		plt.title('Vitesses main gauche')
		plt.plot(tt[save_idx[index]],save_cr[index][0,:],'g',tt[save_idx[index]],save_cr[index][1,:],'r')
		plt.subplot(236)
		plt.xlabel('temps (s)')
		plt.ylabel('vitesses')
		plt.title('Vitesses telephone')
		plt.plot(tk,vxln,'g',tk,vyln,'r')

		plt.show()








app = Appli()
app.mainloop()