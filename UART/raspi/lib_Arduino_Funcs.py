from time import sleep as dormi
from lib_menu import menu_scelta
import serial

#comando in 1 leggi, 2 scrivi, 3 imposta, 4 get impostazione
cmdLeggi=0x01
cmdScrivi=0x02
cmdImpostaModo=0x03
cmdGetModo=0x04

#modo  0 = DigInp, 1=DigInpPullUp, 2=DigOut, 3 = DigOutPWM, 4=AnInp
dummyByte=0x00
DigInp=0x0000
DigInpPullUp=0x0001
DigOut=0x0002
DigOutPWM=0x0003
AnInp=0x0004

debug = False #allows working on development without having Arduino connected

def decodeErrCode(errcode):
    if (errcode==b'\x00')or(errcode==0):
        return('OK')
    elif (errcode==b'\xe1')or(errcode==225):
        return('invalid CRC')
    elif (errcode==b'\xe2')or(errcode==226):
        return('Invalid READ on OUTPUT or Invalid WRITE on INPUT')
    elif (errcode==b'\xe3')or(errcode==227):
        return('not Valid Mode for Pin Number')
    elif (errcode==b'\xe4')or(errcode==228):
        return('invalid Pin Number')
    elif (errcode==b'\xe5')or(errcode==229):
        return('invalid (unknown) Requested Mode')
    elif (errcode==b'\xe6')or(errcode==230):
        return('Error invalid Command ')
    else:
        return('Unknown error code!')

def decodePinNo(PinNo):
    if (PinNo>=0)and(PinNo<=13):
        return(PinNo)
    elif (PinNo==16):
        return("A0")
    elif (PinNo==17):
        return("A1")
    elif (PinNo==18):
        return("A2")
    elif (PinNo==19):
        return("A3")
    elif (PinNo==20):
        return("A4")
    elif (PinNo==21):
        return("A5")
    else:
        return('Unknown PIN number!')

def decodeCmd(cmd):
    if (cmd==b'\x01')or(cmd==1):
        return('Read PIN value Command')
    elif (cmd==b'\x02')or(cmd==2):
        return('Write PIN value Command')
    elif (cmd==b'\x03')or(cmd==3):
        return('Set Mode Command')
    elif (cmd==b'\x04')or(cmd==4):
        return('Get Mode Command')
    if (cmd==b'\x31')or(cmd==49):
        return('Read PIN value Answer')
    elif (cmd==b'\x32')or(cmd==50):
        return('Write PIN value Answer')
    elif (cmd==b'\x33')or(cmd==51):
        return('Set Mode Answer')
    elif (cmd==b'\x34')or(cmd==52):
        return('Get Mode Answer')

    else:
        return('Unknown Command or Answer Code!')

def decodeMode(mode):
    if (mode==b'\x00\x00')or(mode==0):
        return('Digital Input')
    elif (mode==b'\x00\x01')or(mode==1):
        return('Digital Input Pull up')
    elif (mode==b'\x00\x02')or(mode==2):
        return('Digital Output')
    elif (mode==b'\x00\x03')or(mode==3):
        return('Digital Output PWM')
    elif (mode==b'\x00\x04')or(mode==4):
        return('Analogue Input')
    else:
        return('Unknown Mode Code!')

def calcola_CRC(comando): #this works if message is made up as list
    totale = (0x00)
    for i in range(len(comando)):
        comando_int = int.from_bytes(comando[i], byteorder='big')
        totale = totale + comando_int
    return(totale%256)

def CreaDb(db, ser):
    #pin_index_index = 0,     #pin_mode_index = 1,     #pin_value_index = 2
    # 0 = DigInp, 1=DigInpPullUp, 2=DigOut, 3 = DigOutPWM, 4=AnInp
    db.clear()

    if not(debug):
        for i in range(22):
            db.append([ i , GetModo(int(i),ser) , 0])
        print("db", db)
    else:
        for i in range(22):
            db.append([ i , 0 , 0])
        print("db", db)
    return(db)

def decodifica_risposta(ser):
    rcv = b''
    i=1
    totale=0
    while rcv != b'\xf8': #rimetti \xf8
        if not(debug):
            rcv = ser.read()
        else:
            rcv = b'\xf8' #rimetti \xf8
        if (i>1)and(i < 7): #CRC is evaluated only on byte
            totale+=int.from_bytes(rcv,byteorder='big')
        if i==2:
            cmd_fdbck=rcv
        if i==3:
            pinNo_fdbck=rcv
        if (i==4):
            argH=rcv
        if (i==5):
            argL=rcv
        if i==6:
            err_fdbck = rcv
        if i==7:
            CRC_in_fdbck=rcv
        i=i+1
    #print("CRC: ", totale%256, calcola_CRC(answer), " CRC feedback : ", int.from_bytes(CRC_fdbck,byteorder='big')) 
    return([cmd_fdbck,pinNo_fdbck,argH+argL,err_fdbck,CRC_in_fdbck,totale%256])

def TryGetAnswer(ser,cmd,pinNumber,arg,silent=False):
    i = 0
    cmd_fdbck=b''
    pinNo_fdbck=b''
    val_fdbck=b''
    err_fdbck=b''
    CRC_Calc=b'' 
    while ((i==0)or((i < 3)and((int.from_bytes(err_fdbck,byteorder='big')==0xE1)or(int.from_bytes(CRC_in_fdbck,byteorder='big')!=CRC_Calc)))): #this tries up to three times to get a correct answer from Arduino
        #build up message. Message is 0xF7 + command + CRC + 0xF6
        comando2 = 0xF7
        comando2 = comando2<<8
                
        comando2 += cmd
        comando2 = comando2<<8
        CRC = cmd

        comando2 += pinNumber
        comando2 = comando2<<8
        CRC += pinNumber
                 
        comando2 += (arg&65280)>>8
        comando2 = comando2<<8
        CRC += (arg&65280)>>8

        comando2 += arg%256
        comando2 = comando2<<8
        CRC += arg%256

        comando2 += CRC%256
        comando2 = comando2<<8

        comando2 += 0xF6

        if not(silent):
            print("-----------------------------")
        messaggio2=comando2.to_bytes(7, byteorder='big')
        if not(silent):
            print("message sent to Arduino: ",messaggio2)
        if not(debug):
            ser.write(messaggio2)

        #split feedbck (received answer: should be made of command response + err code + received CRC + locally Calculayed CRC for comparison and validation
        if not(debug):
           fdbck=decodifica_risposta(ser)
        else:
           fdbck=[b'\x01', b'\x01', b'\x00', b'\x00', b'\x00', b'\x00']
        cmd_fdbck=fdbck[0]
        pinNo_fdbck=fdbck[1]
        val_fdbck=fdbck[2]
        err_fdbck=fdbck[3]
        CRC_in_fdbck=fdbck[4] #CRC sent by Arduino
        CRC_Calc=fdbck[5] #CRC locally calculated
        if not(silent):
            print("-----------------------------")
            print("Command Anwser: ", cmd_fdbck, int.from_bytes(cmd_fdbck, byteorder='big'), decodeCmd(cmd_fdbck))
            print("Pin Number: ",pinNo_fdbck,int.from_bytes(pinNo_fdbck,byteorder='big'), decodePinNo(int.from_bytes(pinNo_fdbck,byteorder='big')))
            print("Value :",val_fdbck,int.from_bytes(val_fdbck,byteorder='big'))
            print("Error Code: ",err_fdbck,int.from_bytes(err_fdbck,byteorder='big'),decodeErrCode(err_fdbck))       
            print("CRC: ",CRC_in_fdbck, int.from_bytes(CRC_in_fdbck,byteorder='big'))
            print("CRC_Calc: ",CRC_Calc)
            print("-----------------------------")
        i+=1
    if (int.from_bytes(err_fdbck,byteorder='big')==0xE1)or(int.from_bytes(CRC_in_fdbck,byteorder='big')!=CRC_Calc): #225 is 0xE1 corepsonding to CRC error
        return([cmd_fdbck,pinNo_fdbck,val_fdbck,b'\xe1']) #qui devi ancora implementare il valore di ritorno se i tre retry falliscono
    else:
        return([cmd_fdbck,pinNo_fdbck,val_fdbck,err_fdbck])
    
def GetModo(pinNumber,ser,silent=False):
    answer=TryGetAnswer(ser,cmdGetModo,pinNumber,0,silent)
    if not(silent):
        print("GetMode ---- Err in aswer = ", answer[3],decodeErrCode(answer[3]))
    modo=int.from_bytes(answer[2], byteorder='big')
    return(modo)

def LeggiIn(db,ser):
    for i in range(20):
        print("")
    
    ripeti=True
    while ripeti:
        menu_scelta_pinNo=["SELECTION OF PIN NUMBER TO READ","D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13", "", "", "A0", "A1", "A2", "A3", "A4", "A5","Cancel"]
        numeroPinInt = int(menu_scelta(menu_scelta_pinNo,True))

        if not(((numeroPinInt >= 0)and(numeroPinInt <= 13))or(((numeroPinInt >= 16))and(numeroPinInt <= 22))):
            print("PIN number not valid!!!")
            dormi(2)
        else:
            ripeti=False
            if (numeroPinInt==len(menu_scelta_pinNo)-2):
                return(0)
            
    if (((numeroPinInt >= 0)and(numeroPinInt <= 13))or((numeroPinInt >= 16))and(numeroPinInt <= 21)):
        answer=TryGetAnswer(ser,cmdLeggi,numeroPinInt,0)
        print("LeggiDigIn ---- Err in aswer = ", answer[3],decodeErrCode(answer[3]))
        ReadValue=int.from_bytes(answer[2], byteorder='big')
        print("Input value on pin ", numeroPinInt , " is: ",ReadValue)
        print("")
        input("----------[press ENTER to continue]-------------") #pausa riflessiva per mostrare output
        return(ReadValue)   
    else:
        print("Pin number not valid!!!")
        dormi(3) #pausa riflessiva per mostrare messaggio di errore
        return(-1)
    
def ScriviOut(db,ser):
    for i in range(20):
        print(" ")
    ripeti=True
    while ripeti:
        #numeroPin = (int(input("Quale PIN vuole scrivere? > ")))
        menu_scelta_pinNo=["SELECTION OF PIN NUMBER WHERE YOU WANT TO WRITE OUTPUT","D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13", "", "", "A0", "A1", "A2", "A3", "A4", "A5","Cancel"]
        numeroPin = int(menu_scelta(menu_scelta_pinNo,True))
        if not(((numeroPin >= 2)and(numeroPin <= 13))or(((numeroPin >= 16))and(numeroPin <= 22))):
            print("PIN number not valid!!!")
            dormi(2)
        else:
            ripeti=False
            if (numeroPin==len(menu_scelta_pinNo)-2):
                return(0)
            ripeti_in=True
            while ripeti_in:
                try:
                    for i in range(30):
                        print(" ")            
                    valore = (input("What value you want to write [A=Cancel]? > "))
                    if str(valore).upper()=='A':
                        ripeti=True
                        ripeti_in=False
                    else:
                        valore = int(valore)
                        ripeti_in=False
                except ValueError:
                    print('Please insert an integer number......')
                    ripeti_in=True
                  
    if (((numeroPin >= 2)and(numeroPin <= 13))or(((numeroPin >= 16))and(numeroPin <= 22))):
        answer=TryGetAnswer(ser,cmdScrivi,numeroPin,valore)
        print("ScriviOut ---- Err in aswer = ", answer[3],decodeErrCode(answer[3]))
        if not(decodeErrCode(answer[3])=="OK"):
            answer=TryGetAnswer(ser,cmdLeggi,numeroPin,valore)
            ReadValue=int.from_bytes(answer[2], byteorder='big')
            print("Value on pin ", numeroPin, " is: ", ReadValue)
        else:
            ReadValue=int.from_bytes(answer[2], byteorder='big')
            print("Output value on pin ", numeroPin, " is: ", ReadValue)
        print("")
        input("----------[press ENTER to continue]-------------") #pausa riflessiva per mostrare output
        return(ReadValue)
    else:
        print("Pin number you enterd is not valid!!!")
        dormi(3) #pausa riflessiva per mostrare messaggio di errore
        return(-1)

    dormi(1)
    return(0)


def SetPinMode(db,ser):
    for i in range(20):
        print("")
    ripeti=True
    while ripeti:
        menu_scelta_pinNo=["SELECTION OF PIN NUMBER WHOSE MODE YOU WANT TO SET","D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13", "", "", "A0", "A1", "A2", "A3", "A4", "A5","Cancel"]
        numeroPin = int(menu_scelta(menu_scelta_pinNo,True))
        if not((((numeroPin >= 2)and(numeroPin <= 13))or((numeroPin >= 16))and(numeroPin <= 22))):
            print("PIN number not valid!!!")
            dormi(2)
        else:
            ripeti=False
            if (numeroPin==len(menu_scelta_pinNo)-2):
                return(0)

            ripeti_in=True
            while ripeti_in:
                menu_scelta_modo=["SELECTION OF MODE FOR PIN: "+str(decodePinNo(numeroPin))]
                for i in range(5):
                    menu_scelta_modo.append(decodeMode(i))
                menu_scelta_modo.append("Cancel")
                modo=int(menu_scelta(menu_scelta_modo,True))
                if (modo==len(menu_scelta_modo)-2):
                    ripeti=True
                ripeti_in=False          
        
    if ((numeroPin >= 2)and(numeroPin <= 13))or((numeroPin >= 16)and(numeroPin <= 21)):
        answer=TryGetAnswer(ser,cmdImpostaModo,numeroPin,modo)
        if not(decodeErrCode(answer[3])=="OK"):
            answer=TryGetAnswer(ser,cmdGetModo,numeroPin,0)
            ReadValue=int.from_bytes(answer[2], byteorder='big')
            print("Mode of Pin ", numeroPin, " is set to: ", decodeMode(ReadValue))
        else:
            ReadValue=int.from_bytes(answer[2], byteorder='big')
            print("Mode on pin ", numeroPin, " is set to: ", decodeMode(ReadValue))
       
        print("")
        input("----------[press ENTER to continue]-------------") #pausa riflessiva per mostrare output
        return(ReadValue)   
    else:
        print("PIN number you eneterd is not valid!!!")
        dormi(3) #pausa riflessiva per mostrare messaggio di errore
        return(-1)

    dormi(1)
    return(0)

def GetPinMode(db,ser):
    for i in range(20):
        print("")

    ripeti=True
    while ripeti:
        menu_scelta_pinNo=["SELECTION OF PIN NUMBER WHOSE MODE YOU WANT TO KNOW","D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13", "", "", "A0", "A1", "A2", "A3", "A4", "A5","Cancel"]
        numeroPin = int(menu_scelta(menu_scelta_pinNo,True))
        if not( ((numeroPin >= 0)and(numeroPin <= 13))or((numeroPin >= 16)and(numeroPin <= 22)) ):
            print("PIN number not valid!!!")
            dormi(2)
        else:
            ripeti=False
            if (numeroPin==len(menu_scelta_pinNo)-2):
                return(0)

    if (((numeroPin >= 0)and(numeroPin <= 13))or((numeroPin >= 16))and(numeroPin <= 21)):
        answer=TryGetAnswer(ser,cmdGetModo,numeroPin,0)
        ReadValue=int.from_bytes(answer[2], byteorder='big')
        print("Mode of Pin ", numeroPin , " is set to: ", decodeMode(ReadValue))
        print("")
        input("----------[press ENTER to continue]-------------") #pausa riflessiva per mostrare output
        return(ReadValue)   
    else:
        print("Pin number you entered is not valid!!!")
        dormi(3) #pausa riflessiva per mostrare messaggio di errore
        return(-1)

    dormi(1)
    return(0)


def PrintArdStatus(db,ser):
    db1=[]
    for i in range(20):
        print("")
    print("--------------------------------------")
    print("")
    for i in range(22):
        answer=TryGetAnswer(ser,cmdLeggi,i,0,silent=True)
        ReadValue=int.from_bytes(answer[2], byteorder='big')
        db1.append([ i , GetModo(int(i),ser,True) , ReadValue])
        if not((i==14)or(i== 15)):
            print("PIN: " , decodePinNo(db1[i][0]), "--" , "PIN MODE: " , decodeMode(db1[i][1]), "-- Value: ", db1[i][2])
            
    print("")
    
    input("----------[press ENTER to continue]-------------") #pausa riflessiva per mostrare output
    return(0)
