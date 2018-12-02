from time import sleep as dormi

def menu_scelta(menu_items,zerostart=False):
    """ riceve in ingresso una lista con le opzioni da stampare a video. La prima deve essere il titolo del menù e non è un opzione selezionabile dall'utente"""
    ripeti = True
    while ripeti:
        for i in range(20):
            print(" ")

        print("=======================")

        print(menu_items[0])
        for i in range(1,len(menu_items),2):
            if (zerostart==True):
                if (menu_items[i]==""):
                    zerostart=True
                else:
                    if (i< len(menu_items)-1):
                        print(" ",i-1,"> ", menu_items[i],  " ", i, "> ", menu_items[i+1])
                    else:
                        print(" ",i-1,"> ", menu_items[i])
            else:
                if (menu_items[i]==""):
                    zerostart=False
                else:
                    if (i< len(menu_items)-1):
                        print(" ",i,"> ", menu_items[i]," ", i+1, "> ", menu_items[i+1])
                    else:
                        print(" ",i,"> ", menu_items[i])
        print(" ")
        print(" ")
        scelta = input("Your choice> ")

        print("=======================")
            
        try:
            scelta_n = int(scelta)
        except ValueError:
            scelta_n = -1
            print('Please insert an integer number......')
            
        if (zerostart==True):          
            if scelta_n in range(0,len(menu_items)-1):
                ripeti = False
            else: 
                print('Selection not valid')
                dormi(1)
        else:
            if scelta_n in range(1,len(menu_items)):
                ripeti = False
            else: 
                print('Selection not valid')
                dormi(1)           
    for i in range(30):
        print(" ")
    return scelta
