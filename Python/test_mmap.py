import mmap
import time

t1 = time.time()*1000	
print t1
shm = mmap.mmap(0, 512, "Local\\Test") #You should "open" the memory map file instead of attempting to create it..
if shm:
    #shm.write(bytes("5", 'UTF-8'));
    #shm.write(bytes("Hello", 'UTF-8'))
    shm.write_byte(shr(1))
    print("wrote 1")

t2 = time.time()*1000
print t2-t1