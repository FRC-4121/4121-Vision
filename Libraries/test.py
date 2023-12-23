import sys
import time
sys.path.append('/home/pi/.local/lib/python3.7/site-packages')
sys.path.append('/home/pi/Team4121/Libraries')
sys.path.append('/usr/local/lib/vmxpi/')

from vmxpi_hal_python import VMXPi

vmx = VMXPi(False, 50)
print(vmx.isOpen())
time.sleep(15)
print(vmx.isOpen())