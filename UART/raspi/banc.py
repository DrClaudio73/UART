import imaplib
import serial
import time
import random
import logging
ser = serial.Serial()
ser.port = "COM7"
ser.baudrate = 19200
ser.bytesize = serial.EIGHTBITS #number of bits per bytes
ser.parity = serial.PARITY_NONE #set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE #number of stop bits

try: 
    logging.basicConfig(format='%(asctime)s%(levelname)s %(message)s  :',filename='exemple.log',level=logging.DEBUG)
    ser.open()
    
    ser.write("U1,230\r".encode('ascii'))
    ser.write("I1,0\r".encode('ascii'))
    ser.write("W1,0\r".encode('ascii'))
    ser.write("U2,0\r".encode('ascii'))
    ser.write("I2,0\r".encode('ascii'))
    ser.write("W2,0\r".encode('ascii'))
    ser.write("U3,0\r".encode('ascii'))
    ser.write("I3,0\r".encode('ascii'))
    ser.write("W3,0\r".encode('ascii'))
    ser.write("SET\r".encode('ascii'))
    print ("sleep 1 sec")
    time.sleep(10)
   
    
    
except Exception ,e:
    print "error open serial port: " + str(e)
    exit()

ser.close()



  


