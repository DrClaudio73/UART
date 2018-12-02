import serial
from time import sleep as dormi
from lib_menu import menu_scelta
from lib_Arduino_Funcs import CreaDb, LeggiIn, ScriviOut, SetPinMode, GetPinMode, PrintArdStatus
import serial.tools.list_ports

debug = False #allows working on development without having Arduino connected

#MAIN PROGRAM
continua = True
db =[]
ports = list(serial.tools.list_ports.comports())

baudrate=9600 #keep a default baudrate
useDefaultUART="No"
defaultUART="/dev/ttyS0"

f = open('config_IfArduino.txt', 'r')
with f:
	configurazione=f.readlines()

for linea in configurazione:
	if "baudrate" in linea: baudrate=int(linea.strip("baudrate="))
	if "useDefaultUART" in linea: 
		if "Yes" in linea: useDefaultUART="Yes"	
	if "default_UART" in linea: defaultUART=linea.strip("default_UART= ") 
print(baudrate)
print(useDefaultUART)
print(defaultUART)

#if not(useDefaultUART=="Yes")
menu_scelta_UART=["SELECTION OF SERIAL PORT NUMBER TO USE"]
lx_win = "windows"

for p in ports:
    #print(p)
    #print(p[0])
    #print("DESCRIPTION: ",p.description)
    #print("NAME: ",p.name)
    menu_scelta_UART.append(p.description)
    #print("device: ",p.device)
    #print("type:", type(p.device))
    #print("ports:", type(ports))
    #if ('/dev/' in p.device): print("typeif:", type(p.device))
    if ('/dev/tty' in p.device): lx_win="Linux"
    
if (lx_win=="Linux"):
	menu_scelta_UART.append("/dev/ttyS0")
    
"""
arduino_ports = [
    p.device
    for p in serial.tools.list_ports.comports()
    if 'tty' in p.description
]

print("ports",arduino_ports)
"""
#input("avanti")
menu_scelta_UART.append("Cancel")
ripeti=True

while ripeti:
	numeroUART = int(menu_scelta(menu_scelta_UART,True))
	ripeti=False
	if (numeroUART==len(menu_scelta_UART)-2):
		print("Goodbye!!! ")
		exit(0)

if not(debug):
	if menu_scelta_UART[numeroUART+1]=="/dev/ttyS0":
		ser = serial.Serial("/dev/ttyS0", baudrate, timeout=3)
	else:
		ser = serial.Serial(ports[numeroUART].device, baudrate, timeout=3)
	
	ser.reset_input_buffer()
	print("Port Name: ",ser.name)
	print("Port details: ", ser)
	#input("avanti")
else:
    ser = 0 
    
if not(menu_scelta_UART[numeroUART+1]=="/dev/ttyS0"):
	dormi(2) #let Arduino get started!

CreaDb(db,ser)

while continua:
    main_menu=["FUNCTION SELECTION","Read an input","Write output","Set Pin Mode","Get Pin Mode","Show Arduino I/O status","Exit"]
    scelta = menu_scelta(main_menu)
    funcs = {'1':LeggiIn, '2':ScriviOut,  '3':SetPinMode, '4':GetPinMode, '5':PrintArdStatus}
    
    if int(scelta,10) in range(len(main_menu)-1):
        func = funcs[scelta]
        res = func(db,ser)
    else:
        print("Goodbye!!! ")
        continua = False

if not(debug):
    ser.close()