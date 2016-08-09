import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate
from scipy import signal

def normaliser2(a,b):
	maxi = max(abs(a).max(),abs(b).max())
	return a/maxi, b/maxi


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
tt = np.linspace(0,min(max(tk),max(tsm)),num=round(max(tsm))*50)
#print tt.shape

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
for delta in range(0,-deltamax-1,-1):
	
	idx = np.arange(tt.size+delta)
	cl = np.roll(v_left,delta)[:,idx]
	cr = np.roll(v_right,delta)[:,idx]
	csm = v_sm[:,idx]

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

print "Main gauche dist: ", dist_left
print "Main droite dist : ", dist_right

if dist_left<dist_right:
	dist_right = diff_r[dist_left_idx]
	print "===========> main GAUCHE"
	print "Main gauche dist: ", dist_left
	print "Main droite dist : ", dist_right
else:
	dist_left = diff_l[dist_right_idx]
	print "===========> main DROITE"
	print "Main gauche dist: ", dist_left
	print "Main droite dist : ", dist_right

plt.show()





