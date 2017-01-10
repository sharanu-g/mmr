from flask import Flask,render_template
import subprocess
import os
from flask import request
from time import sleep


app = Flask(__name__)

name1 = "1"
name2 = "50"
one = "one"
two = "two"
three = "three"
four = "four"
@app.route('/poweroff')
def poweroff():
      subprocess.Popen("sudo shutdown -P now",stdout=subprocess.PIPE,shell=True)
      return 'poweroff'

@app.route('/reboot')
def reboot():
    subprocess.Popen("sudo shutdown -r now",stdout=subprocess.PIPE,shell=True)
    return 'reboot'

@app.route('/change_pass')
def psw():
       ch = request.args['psw']
       print ch
       f = open("local1.txt","rw+")
       txt = f.read()
       f.close()

       f1 = open("/etc/rc.local","w")
       password = ch
       t = "\nsudo ap recto-virus "+password+"\nexit 0"
       txt = txt+t
       f1.write(txt)
       f1.close()
       print "System is going to restart now"
       sleep(5)
       subprocess.Popen("sudo shutdown -r now",stdout=subprocess.PIPE,shell=True)
       return 'psw changed'


       

@app.route('/progress')
def index():
 #checking for external device connected or not
       output = subprocess.Popen("lsblk",stdout=subprocess.PIPE,shell=True)
       usb_list = ["usb1","usb2"]
       i=0
    	#if media text found 
       for out in output.communicate()[0].split():
    		if '/media/' in out:
        		usb_list[i] = out
       		        i = i+1
       us = usb_list[0]
       us = us[0:17]
       int_card = "df -k "+'/'
       ext_card = "df -k "+usb_list[0]
       if us == '/media/pi/SETTING':
           print 'no extenal memory'
           found = 0
           rang = 1
       else:
           print "external device is at: ",usb_list[0]
           found = 1
           rang = 2

       for i in range(rang):
            if i == 0:
               card = int_card
            elif i == 1:
                card = ext_card
            output = subprocess.Popen(card,stdout=subprocess.PIPE,shell=True)
            out = output.communicate()[0].replace("  "," ")
            out = out.replace("  "," ")
            out = out.replace("  ","")
            out = out.split(' ')
            #print out
            ou = out[5]
            ou = ou[12:]
            max1 = ou
            min1 = out[6] 
     

            ch1 = out[6]
            ch2 = ou
       
            ou = float(out[7])
            ou = ou/1024/1024
            ou = round(ou,2)
            ch3 = str(ou)

            ou = float(ch2)
            ou = ou/1024/1024
            ou = round(ou,2)
            ch4 = str(ou)

            ch5 = ch4

            ou = float(out[6])
            ou = ou/1024/1024
            ou = round(ou,2)
            ch6 = str(ou)
       
            ch7 = ch3
            ch8 = out[8]
            if i == 0:
                name1 = ch1
                name2 = ch2
                name3 = ch3
                name4 = ch4
                one = ch5
                two = ch6
                three = ch7
                four  = ch8
            if i == 1:
                name5 = ch1
                name6 = ch2
                name7 = ch3
                name8 = ch4
                five = ch5
                six = ch6
                seven = ch7
                eight = ch8
            #print name

    #   name = "returned Successfully"
       if found == 1:
           return render_template('index.html', name1=name1,name2=name2,name3=name3,name4=name4,one=one,two=two,three=three,four=four,name5=name5,name6=name6,name7=name7,name8=name8,five=five,six=six,seven=seven,eight=eight)
       elif found == 0:
            return render_template('index1.html', name1=name1,name2=name2,name3=name3,name4=name4,one=one,two=two,three=three,four=four)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=80)
