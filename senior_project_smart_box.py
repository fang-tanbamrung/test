#!/usr/bin/env python
from threading import Timer 
import time
import random
import os
import I2C_LCD_driver
from pyfingerprint.pyfingerprint import PyFingerprint
import hashlib
import RPi.GPIO as GPIO
from picamera.array import PiRGBArray
from picamera import PiCamera
import sys
import cv2
from datetime import datetime
from multiprocessing import Process, Manager
from threading import Timer
from test_sound import sound
import zbar
import numpy as np
from PIL import Image
import MySQLdb




    
class test:         #��ͻ������Ѻ����觢����ż�ҹ�Ź�
    def __init__(self, msg):
        self.msg = str(msg)
        

    
    
    def send(self):
        os.system("curl -X POST https://notify-api.line.me/api/notify \
        -H 'Authorization: Bearer XqX5jjnMmStCGkZ2ZFnLjJ3Bnx7jOPFHJJUdWEyN8Wv' \
        -F 'message= %s' \  "%self.msg)
        

def closeLockf():       #��͡��еٴ�ҹ˹��
    GPIO.output(frontlock, GPIO.HIGH)

def openLockf():        #�Ŵ��͡��еٴ�ҹ˹��
    #crsound()          
    GPIO.output(redf, GPIO.LOW)     #���ᴧ�Ѻ
    GPIO.output(greenf, GPIO.HIGH)  #������ǵԴ
    a = 0                           
    GPIO.output(frontlock, GPIO.LOW)#�Ŵ��͡��͹��ҹ˹��
    #blink(greenf)
    time.sleep(3)    
    while True:
        time.sleep(0.5)
        
        i = GPIO.input(frontsen)    #��Ǩ�Ѻ��һ�еٻԴʹԷ�����������
        if i == 1:                  #��е��ѧ�Դ���ʹԷ
            a = a+1
            if a == 30:
                print'pls close the door'
                #closeSound()
                a = 0
            
        elif i == 0:                #��еٻԴʹԷ����
            
            closeLockf()            #��͡��͹��е�
            
            break
    GPIO.output(greenf, GPIO.LOW)   #LED �����ǴѺ


def closeLockb():                   #��͡��еٴ�ҹ��ѧ
    GPIO.output(backlock, GPIO.HIGH)   

def openLockb():                #�Ŵ��͡��еٴ�ҹ��ѧ
    #crsound()
    GPIO.output(greenb, GPIO.HIGH)  #LED �����ǵԴ
    a = 0
    GPIO.output(backlock, GPIO.LOW) #�Ŵ��͡��͹
    #blink(greenf)
    time.sleep(3)                   
    while True:                 
        time.sleep(0.5)
        
        i = GPIO.input(backsen)     #��Ǩ��һ�еٻԴʹԷ�������
        if i == 1:                  #��е��ѧ�Դ���ʹԷ
            a = a+1
            if a == 30:
                print'pls close the door'
                #closeSound()
                a = 0
            
        elif i == 0:                #��еٻԴʹԷ����
            
            closeLockb()            #��͡��͹��е�
            
            break
    GPIO.output(greenb, GPIO.LOW)   #LED �����Ǵ�ҹ��ѧ�Ѻ
        
            
def blink(led):                     #LED ��о�Ժ
    for i in range(5):
        GPIO.output(led, GPIO.LOW)
        time.sleep(0.3)
        GPIO.output(led, GPIO.HIGH)
        time.sleep(0.3)


def barcode(state):                 #����ͧ�������ҹ������
    #scsound()
    while True:
        
        db = MySQLdb.connect(host ='192.168.94.64', user = 'rpi', passwd =  '', db = 'test')                        ############################          
                                                                                                                    ## ���ҧ��ͺ��㹡�����¡��ҹ������ ##
        cur = db.cursor()                                                                                           ############################
                                                                                                                
        cur.execute("SELECT trackid FROM ems2")                                                     #���͡�ҹ������㹡����ҹ������

        cap = cv2.VideoCapture(0)                                                                   #��ҹ�Ҿ�ҡ���ͧ�����
        scanner = zbar.ImageScanner()                                                               #���ҧ��ͻ��㹡����ҹ������
        scanner.parse_config('enable')
        
        while(cap.isOpened()):
            
            endp = True
            end = 0 
            ret, img = cap.read()   
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)                                            #�ç������
            pil = Image.fromarray(gray)
            width, height = pil.size
            raw = pil.tobytes()                                                                     #�ŧ�Ҿ���������͵�Ǩ�Ѻ������
            image = zbar.Image(width, height, 'Y800', raw)
            scanner.scan(image)                                                                     #�ʡ��ç��ǹ����繺�����
            

            for symbol in image:    
                print ' decoded', symbol.type, 'symbol', "'%s'"%symbol.data

                for row in cur.fetchall():                                                          #��ҹ���ʺ����鴨ҡ�ҹ�����ŷ�����
                    trackid = str(row[0])
                    
                    if symbol.data == trackid:                                                      #���ʵç�Ѻ�ҹ������
                        print 'code is correct'
                        cur.execute("DELETE FROM ems2 WHERE trackid = '" +trackid+ "'")             #ź���ʷ��ç�Ѻ�ҹ�������͡�ҡ���ҧ�����ҹ��
                        cur.execute("UPDATE ems SET status=%s WHERE trackid=%s",('recieved', trackid))      #�ѻവ������ʷ��ç�Ѻ���������Ѻ����
                        db.commit()
                        end = 2
                        endp = False
                        
                        break
                if end == 0:                                                                        
                    #scasound()
                    end = 1                                                                         
                                       
                    
                    break
            
            if end == 1:                                                                            #����������١��ͧ LED ��ᴧ�С�о�Ժ �����觢�ͤ�����ҹ�Ź�
                msg = "package number is not correct"
                a = test(msg)
                a.send()
                blink(redf)
                endp = False
                break
            if end == 2:                                                                            #������ʶ١��ͧ ��е٨��Դ�͡�������ͻԴ���觢�ͤ�����Ҿ�ʴص�������Ţ���Ѻ����
                #crsound()
                msg = "package number "+str(symbol.data)+' received'
                a = test(msg)
                openLockf()
                a.send()                         
                break        
                                            
            cv2.imshow('img',img)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                    break
            
        
        cur.close()
        db.close()
        cap.release()
        cv2.destroyAllWindows()
        if endp == False:            
            break
    GPIO.output(redf, GPIO.LOW)
    
    state[0] = 1                                                                                    #����¹��Ңͧ��������ͺ͡ʶҹ���Ҩ���������        
    
    

def picam(state):               #�ѹ�֡�մ��ʹ��¡��ͧ Raspberrry Pi 
    
    DEBUG = False
    if len(sys.argv) > 1:
        DEBUG = sys.argv[-1] == 'DEBUG'

    
    FULLSCREEN = not DEBUG
    if not DEBUG:
        RESOLUTION = (640,480)
    else:
        RESOLUTION = (480,270)

    
    dt = datetime.now()

    camera = PiCamera()
    camera.resolution = RESOLUTION
    fourcc = cv2.cv.FOURCC(*'XVID')
    out = cv2.VideoWriter("Video%s.avi"%dt ,fourcc,30.0,(640,480))
    camera.framerate = 50

    rawCapture = PiRGBArray(camera, size=RESOLUTION)

    time.sleep(0.1)
    print'Picamera ready'

    for frame in camera.capture_continuous(rawCapture, format = 'bgr',use_video_port = True):
        
        img = frame.array.copy()
        output = cv2.flip(img,0)    
        cv2.imshow('Picamera',output)
        out.write(output)
        
        rawCapture.truncate(0)
        
        keypress = cv2.waitKey(1) & 0xFF
        if keypress == ord('q'):
            break
        if state[0] == 1:                                                                       #����÷ӧҹ����͡����ҹ��������������
            break

    camera.close()
    out.release()
    cv2.destroyAllWindows()

def scsound():                                                                                  #������§����ʡ�������         
    while True:
        sc = sound('/home/pi/project/Scan.mp3')
        sc.start()
        break

def scasound():                                                                                 #������§��Һ����鴼Դ����ʡ�����
    while True:
        inc = sound('/home/pi/project/Incorrect.mp3')
        sca = sound('/home/pi/project/Scan-Again.mp3')
        inc.start()
        sca.start()
        break

def crsound():                                                                                  #������§��Һ����鴶١��ͧ
    while True:
        cr = sound('/home/pi/project/Correct.mp3')
        cr.start()
        break

def closeSound():                                                                               #������§���Դ��е�
    while True:
        cd = sound('/home/pi/project/closedoor.mp3')
        cd.start()
        break


if __name__ == '__main__':

    
    
    tl = 'Too Late'
    startran = 9999
    stopran = 99999
    TO = 30
    
    backs = 21
    fronts = 20
    backsen = 26
    frontsen = 13
    backlock = 6
    frontlock = 19
    frontTimeout = 5
    greenf = 17
    greenb = 27
    redf = 16
    redb = 22

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(backs, GPIO.IN, pull_up_down = GPIO.PUD_UP) 
    GPIO.setup(fronts, GPIO.IN, pull_up_down = GPIO.PUD_UP) 
    GPIO.setup(backsen, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(frontsen, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(backlock, GPIO.OUT)
    GPIO.setup(frontlock, GPIO.OUT)
    GPIO.setup(greenf, GPIO.OUT)
    GPIO.setup(greenb, GPIO.OUT)
    GPIO.setup(redf, GPIO.OUT)
    GPIO.setup(redb, GPIO.OUT)
    GPIO.output(redf, GPIO.LOW)
    GPIO.output(redb, GPIO.LOW)
    GPIO.output(greenf, GPIO.LOW)
    GPIO.output(greenb, GPIO.LOW)
    GPIO.output(backlock, GPIO.HIGH)
    GPIO.output(frontlock, GPIO.HIGH)
 
    lcd = I2C_LCD_driver.lcd()

    lcd.lcd_clear()
    lcd.lcd_display_string('ready!', 1, 5)
    time.sleep(3)
    lcd.lcd_clear()
    
    
    
    
    
    while True:
        
        def tl():                                                                   #�ѧ����������Թ����㹡��������� OTP
            print'\ntoo late\n'
            lcd.lcd_clear()
            lcd.lcd_display_string('Too late', 1, 4)
            lcd.lcd_display_string('press  enter', 2, 2)
            
        backswitch = GPIO.input(backs)
        frontswitch = GPIO.input(fronts)

        dt = datetime.now()
        dts = dt.timetuple()
        trm = dts[0] - 1
        os.system("rm -f Video"+str(trm)+"*")

        

            
        if backswitch == 0:                                                         #�����Է���ҹ��ѧ�١�����ʴ���ͤ���������͡������ҧ��� 1.�Դ��е� 2.������¹������ 3.ź��¹������
            
            GPIO.output(redb, GPIO.HIGH)
            lcd.lcd_clear()
            lcd.lcd_display_string('Choose Number:', 1, 1)
            lcd.lcd_display_string('1.Open2.Add3.Del', 2)
            try:
                
                backprogram = input('choose program: ')
                    
                while True:
                    
                    

                    if backprogram == 1:                                                                    #��������͡�Դ��е�
                        
                        try:                                                                                #�������������͡Ѻ������ʡ���¹������
                            f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

                            if(f.verifyPassword() ==False):
                                raise ValueError('The given fingerprint sensor password is wrong')
                        except Exception as e:
                            print('The fingerprint sensor couldnot be initialized')
                            print('Exception message:' + str(e))
                            
                            lcd.lcd_clear()
                            lcd.lcd_display_string('fingerprint', 1, 1)
                            lcd.lcd_display_string('sensor error', 2, 1)
                            exit(1)
                                                                                                            #��������ҹ��¹������������º�Ѻ���������
                        try:
                            count = 0
                            while count < 5:
                                lcd.lcd_clear()
                                lcd.lcd_display_string('WaitinG finGer', 1, 1)
                                                                                                            #����¹������
                                while (f.readImage() == False):
                                    pass
                                f.convertImage(0x01)

                                                                                                            #�觼š�ä��������㹵���� result
                                result = f.searchTemplate()
                                positionNumber = result[0]
                                accuracyScore = result[1]
                                
                                if (positionNumber == -1):                                                  #�����¹���������ç�Ѻ�����������ʴ���ͤ��������辺
                                    lcd.lcd_clear()
                                    lcd.lcd_display_string('Not match!', 1, 3)
                                    time.sleep(3)
                                    lcd.lcd_clear()
                                    count = count + 1
                                    
                                else:                                                                       #�����¹�����͵ç�Ѻ�����������ʴ���������ӡѺ��¹�����ͷ��������
                                    lcd.lcd_clear()
                                    lcd.lcd_display_string('Correct! #'+str(positionNumber), 1, 2)
                                    lcd.lcd_display_string('Acuracy: '+str(accuracyScore), 2, 2)
                                    time.sleep(2)
                                    lcd.lcd_clear()
                                    break

                        except Exception as e:
                            lcd.lcd_clear()
                            lcd.lcd_display_string('failed', 1, 5)
                            lcd.lcd_display_string(str(e), 2)
                            print('Exception message'+str(e))
                            exit(1)

                        if count >= 5:
                            break
                        

                        #��ǹ OTP
                        loopcount = 0
                        while True:
                            if loopcount >= 5:
                                break
                            
                            OTP = random.randint(startran, stopran)                 ##############
                            msg = 'OTP = '+ str(OTP)                                ##          ##
                            a = test(msg)                                           ## ������ OTP ##
                            a.send()                                                ##          ##
                            timer = Timer(TO, tl)                                   ##############
                            timer.start()
                            try:
                                lcd.lcd_clear()                                 ################
                                lcd.lcd_display_string('enter Password:', 1)    ### ������ OTP ###
                                inputpassword = input('enter password: ')       ################

                                if inputpassword == OTP:                        #������� OTP �١�зӡ�ûŴ��͡��е�����������еٻԴʹԷ������͡
                                    lcd.lcd_display_string('Correct!', 2, 5)
                                    timer.cancel()
                                    time.sleep(1)
                                    lcd.lcd_clear()
                                    lcd.lcd_display_string('Open', 1, 5)
                                    GPIO.output(redb, GPIO.LOW)
                                    openLockb()
                                    lcd.lcd_clear()                                                                   
                                    break
                                
                                elif inputpassword != OTP:                      #������� OTP ���١��ͧ�зӡ���������ա 4 ����
                                    lcd.lcd_display_string('Incorrect!', 2, 3)
                                    timer.cancel()
                                    time.sleep(3)
                                    lcd.lcd_clear()
                                    loopcount += 1
                            except SyntaxError:
                                timer.cancel()
                                print'Try again'
                        
                        break
                        
                    if backprogram == 2:                                                            #��������͡������¹������
                        
                        try:                                                                        #�������������͡Ѻ������ʡ���¹������
                            f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

                            if(f.verifyPassword() == False):
                                raise ValueError('The given fingerprint sensor password is wrong')

                        except Exception as e :
                            print('The fingerprint sensor couldnot be initialized')
                            print('Exception message:' + str(e))
                            #display to lcd
                            lcd.lcd_clear()
                            lcd.lcd_display_string('fingerprint', 1, 1)
                            lcd.lcd_display_string('sensor error', 2, 1)
                            exit(1)

                                                                                                    
                        try:
                                                                                                    #��Ǩ�ͺ�������¹������ ������������������
                            tableIndex = f.getTemplateIndex(0)
                            if tableIndex[0] == False:                                              #�ҡ����ը����ӡ�����ҧ��¹�����������������
                                print'Create Master finger'
                                lcd.lcd_clear()
                                lcd.lcd_display_string('Add Master', 1, 4)
                                
                                while (f.readImage() == False):
                                    pass

                                
                                f.convertImage(0x01)

                                
                                result = f.searchTemplate()
                                positionNumber = result[0]

                                if(positionNumber >= 0 ):
                                    lcd.lcd_clear()
                                    lcd.lcd_display_string('Already exist!',  1, 1)
                                    time.sleep(3)
                                    lcd.lcd_clear()
                                    GPIO.output(redb, GPIO.LOW)
                                    break

                                lcd.lcd_display_string('Remove finGer!', 1, 1)
                                time.sleep(3)

                                lcd.lcd_clear()
                                lcd.lcd_display_string('Put Again', 1, 3)

                                
                                while(f.readImage() == False):
                                    pass
                                
                                
                                f.convertImage(0x02)

                                
                                
                                if (f.compareCharacteristics() == 0):
                                    lcd.lcd_clear()
                                    lcd.lcd_display_string('Not match!', 1, 3)
                                    time.sleep(3)
                                    lcd.lcd_clear()
                                    GPIO.output(redb, GPIO.LOW)
                                    
                                    break    
                                
                                f.createTemplate()

                                
                                f.storeTemplate()
                                lcd.lcd_clear()
                                lcd.lcd_display_string('Successfully', 1, 2)
                                time.sleep(5)
                                lcd.lcd_clear()
                                
                                

                            else:                                                           #�ҡ����¹�����ͨзӡ�õ�Ǩ��¹�����͡Ѻ��¹�������������
                                
                                lcd.lcd_clear()
                                lcd.lcd_display_string('Master finGer', 1, 1)

                                
                                while(f.readImage() == False):
                                    pass
                                
                                f.convertImage(0x01)
                                
                                
                                result = f.searchTemplate()
                                positionNumber = result[0]
                                accuracyScore = result[1]
                                
                                if(positionNumber != 0):
                                    lcd.lcd_clear()
                                    lcd.lcd_display_string('Not match', 1, 3)
                                    time.sleep(5)
                                    lcd.lcd_clear()
                                    GPIO.output(redb, GPIO.LOW)
                                    break
                                else:
                                    lcd.lcd_clear()
                                    lcd.lcd_display_string('Correct!', 1, 4)
                                    lcd.lcd_display_string('accuracy: '+str(accuracyScore), 2, 2)
                                    time.sleep(3)

                        except Exception as e:
                            lcd.lcd_clear()
                            lcd_display_string('Error Occur!', 1, 2)
                            print('Exception message'+str(e))
                            exit(1)

                        
                        try:                                                        #��������������¹������
                            lcd.lcd_clear()
                            lcd.lcd_display_string('Waiting finGer', 1, 1)
                            
                            while (f.readImage() == False):
                                pass
                           
                            f.convertImage(0x01)

                            
                            result = f.searchTemplate()
                            positionNumber = result[0]

                            if(positionNumber >= 0 ):
                                lcd.lcd_clear()
                                lcd.lcd_display_string('Already exist!',  1, 1)
                                time.sleep(3)
                                lcd.lcd_clear()
                                GPIO.output(redb, GPIO.LOW)
                                break

                            lcd.lcd_display_string('Remove finGer!', 1, 1)
                            time.sleep(3)

                            lcd.lcd_clear()
                            lcd.lcd_display_string('Put Again', 1, 3)

                            
                            while(f.readImage() == False):
                                pass
                            
                            
                            f.convertImage(0x02)

                            
                            
                            if (f.compareCharacteristics() == 0):
                                lcd.lcd_clear()
                                lcd.lcd_display_string('Not match!', 1, 3)
                                time.sleep(3)
                                
                                GPIO.output(redb, GPIO.LOW)
                                break

                            
                            f.createTemplate()

                            
                            f.storeTemplate()
                            lcd.lcd_clear()
                            lcd.lcd_display_string('Successfully', 1, 2)
                            time.sleep(5)
                            lcd.lcd_clear()
                            GPIO.output(redb, GPIO.LOW)

                        except Exception as e:
                            lcd.lcd_clear()
                            lcd.lcd_display_string('Failed!', 1, 5)
                            print('Exception message: ' + str(e))
                            time.sleep(3)
                            lcd.lcd_clear()
                            exit(1)

                        
                        break
                
                    if backprogram == 3:                                                            #��������͡�����ź��¹������
                        
                        
                        try:                                                        
                            f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

                            if (f.verifyPassword() == False):
                                raise ValueError('The given fingerprint sensor password is wrong')
                        except Exception as e:
                            print('The fingerprint sensor couldnot be initialized')
                            print('Exception message:' + str(e))
                            #display to lcd
                            lcd.lcd_clear()
                            lcd.lcd_display_string('fingerprint',1,1)
                            lcd.lcd_display_string('sensor error',2,1)
                            exit(1)

                        
                        try:                                                                        #��Ǩ�ͺ�������¹��������������������
                            
                            tableIndex = f.getTemplateIndex(0)
                            if tableIndex[0] == False:
                                print'Create Master finger'
                                lcd.lcd_clear()
                                lcd.lcd_display_string('Add Master', 1, 4)
                                
                                while (f.readImage() == False):
                                    pass

                                f.convertImage(0x01)

                                result = f.searchTemplate()
                                positionNumber = result[0]

                                if(positionNumber >= 0 ):
                                    lcd.lcd_clear()
                                    lcd.lcd_display_string('Already exist!',  1, 1)
                                    time.sleep(3)
                                    lcd.lcd_clear()
                                    GPIO.output(redb, GPIO.LOW)
                                    break

                                lcd.lcd_display_string('Remove finGer!', 1, 1)
                                time.sleep(3)

                                lcd.lcd_clear()
                                lcd.lcd_display_string('Put Again', 1, 3)

                                while(f.readImage() == False):
                                    pass
                                
                                f.convertImage(0x02)

                                if (f.compareCharacteristics() == 0):
                                    lcd.lcd_clear()
                                    lcd.lcd_display_string('Not match!', 1, 3)
                                    time.sleep(3)
                                    lcd.lcd_clear()
                                    GPIO.output(redb, GPIO.LOW)
                                   
                                    break

                                f.createTemplate()

                                f.storeTemplate()
                                lcd.lcd_clear()
                                lcd.lcd_display_string('Successfully', 1, 2)
                                time.sleep(5)
                                lcd.lcd_clear()
                                

                            else:
                                
                                lcd.lcd_clear()
                                lcd.lcd_display_string('Master finGer', 1, 1)

                                
                                while(f.readImage() == False):
                                    pass
                                
                                f.convertImage(0x01)
                            
                                
                                result = f.searchTemplate()
                                positionNumber = result[0]
                                accuracyScore = result[1]
                                
                                if(positionNumber != 0):
                                    lcd.lcd_clear()
                                    lcd.lcd_display_string('Not match', 1, 3)
                                    time.sleep(3)
                                    lcd.lcd_clear()
                                    GPIO.output(redb, GPIO.LOW)
                                    break
                                else:
                                    lcd.lcd_clear()
                                    lcd.lcd_display_string('Correct!', 1, 4)
                                    lcd.lcd_display_string('accuracy: '+str(accuracyScore), 2, 2)
                                    time.sleep(3)

                        except Exception as e:
                            lcd.lcd_clear()
                            lcd.lcd_display_string('Error Occur!', 1, 2)
                            print('Exception message'+str(e))
                            exit(1)

                        print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

                        try:
                            lcd.lcd_clear()
                            lcd.lcd_display_string('Enter index:', 1, 2)
                            positionNumber = input('Please enter the template position you want to delete: ')
                            positionNumber = int(positionNumber)

                            if ( f.deleteTemplate(positionNumber) == True ):
                                print('Template deleted!')
                                lcd.lcd_clear()
                                lcd.lcd_display_string('Deleted!', 1, 4)
                                time.sleep(3)
                                lcd.lcd_display_string(str(f.getTemplateCount())+'finGer left', 1, 1)
                                time.sleep(2)
                                lcd.lcd_clear()
                                

                        except Exception as e:
                            print('Operation failed!')
                            print('Exception message: ' + str(e))
                            exit(1)
              
                        GPIO.output(redb, GPIO.LOW)
                        break
                    else:
                        lcd.lcd_clear()
                        lcd.lcd_display_string('Choose 1-3', 1, 3)
                        time.sleep(2)
                        lcd.lcd_display_string('Press button', 1, 2)
                        time.sleep(1)
                        lcd.lcd_clear()
                        GPIO.output(redb, GPIO.LOW)
                        break
                
            except SyntaxError:
                lcd.lcd_clear()
                lcd.lcd_display_string('Press button', 1, 2)
                time.sleep(2)
                lcd.lcd_clear()
                GPIO.output(redb, GPIO.LOW)

        if frontswitch == 0:
            while True:
                GPIO.output(redf, GPIO.HIGH)
                manager = Manager()
                state = manager.dict()
                state[0] = 0
                p1 = Process(target = barcode, args = (state,))             #���ҧ��ͻ������㹡���ʡ�������
                p2 = Process(target = picam, args = (state,))               #���ҧ��ͻ������㹡�úѹ�֡�մ���
                
                    
                scsound()                                                   #������§����ʡ�������
                p1.start()                                                  #�����������ҹ������
                p2.start()                                                  #��������ʺѹ�֡�մ���
                print state
                p1.join()
                print state
                p2.join()
                break
            
