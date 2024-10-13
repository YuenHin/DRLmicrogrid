
import time
for i in range(1000):
    time.sleep(1)
    print('\r', {'i':'%d'%i}, end = '', flush = True)