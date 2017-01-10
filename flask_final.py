import signal
from signal import signal,SIGPIPE,SIG_DFL
import thread
import sys
import warnings
from collections import namedtuple
import threading
import re
import os,sys,time,io
import subprocess
from flask import Flask,render_template,Response
from flask import request
from time import sleep
import picamera
import RPi.GPIO as GPIO
from flask import request
from flask.ext.autoindex import AutoIndex
from fpdf import FPDF,HTMLMixin

title = 'Vision medical     '
patient_img_dir = "/home/sharan/"
patient_vid_dir = "/home/sharan/"
storage = "/media/pi/internal/"
add = "hel"
pdf = "Location"
cnt = 0
split_count = 1
cam_status = 0
recent_h264 = "/media/pi/internal"
regex = re.compile("^[a-zA-Z0-9#@-_&/?=:% $]+$")

app = Flask(__name__)
AutoIndex(app, browse_root='/media/pi/')

def convert_video(rtn_name):
        global cnt
        global split_count
        cnt += 1
        #print "cnt,split_count",cnt,split_count
	 #print "Converting video thread started..."
	in_file = patient_vid_dir+"video"+str(split_count)+".h264 "
	out_file = patient_vid_dir+"video"+str(cnt)+".mp4"
        print "split-video converting to mp4"
        card = "sudo MP4Box -fps 30 -add "+in_file+out_file                
        #print "Converting please wait"
        #print "Converting command is:",card
        #print "in_file",in_file
        #print "Out file",out_file

        try:
                output = subprocess.Popen(card,stdout=subprocess.PIPE,shell=True)
                out = output.communicate()[0]
                if out == "":
                        card = "sudo rm "+in_file
                        output = subprocess.Popen(card,stdout=subprocess.PIPE,shell=True)
                        out = output.communicate()[0]
                        #print "Converted successfully"
                        print "Converting video thread terminated..."
                        #print rtn_name
                        return rtn_name
        except:
                print "Error in split-video converting"


def stop_convert_video(fil):
        global patient_vid_dir
        global recent_h264

        #print "cnt",cnt
	#print "Converting stop video thread started..."
	out_file = patient_vid_dir+"last.mp4"

        card = "sudo MP4Box -fps 30 -add "+recent_h264+" "+out_file
                
        #print "stop Converting command is:",card
        #print "Out file",out_file

        try:
                output = subprocess.Popen(card,stdout=subprocess.PIPE,shell=True)
                out = output.communicate()[0]
                if out == "":
                        card = "sudo rm "+recent_h264
                        output = subprocess.Popen(card,stdout=subprocess.PIPE,shell=True)
                        out = output.communicate()[0]
                        print "Converted successfully"
                        #print "Converting video thread terminated..."
                        return fil
        except:
                print "Error in stop-video converting"
                

class Camera(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera




    def initialize(self):          
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()
	
            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        return self.frame

    @classmethod
    def _thread(cls):
        try:
         with picamera.PiCamera() as camera:
            # camera setup
            camera.resolution = '1080p'  
            camera.sharpness = 0
            camera.contrast = 0
            camera.brightness = 60
            camera.saturation = 0
            camera.ISO = 0
            camera.video_stabilization = False
            camera.exposure_compensation = 0
            camera.exposure_mode = 'auto'
            camera.meter_mode = 'average'
            camera.awb_mode = 'auto'
            camera.image_effect = 'none'
            camera.color_effects = None
            camera.rotation = 0
            camera.hflip = False
            camera.vflip = False
            camera.crop = (0.0, 0.0, 1.0, 1.0)
            #camera.start_preview()

            time.sleep(2)
            
            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # store frame

                global count
                global cnt
                global img_count
                global patient_vid_dir
                global split_count
                global cam_status
                global recent_h264
                if count == 12:
                    if camera.recording:
                        print "recording started already"
                        count = 0
                    else:
                        cam_status = 1
                        cnt = 0
                        split_count = 1
                        recent_h264 = patient_vid_dir+'video1.h264'
                        camera.start_recording(recent_h264)
                        
                        GPIO.output(10,GPIO.HIGH) 
                        disk_check()
                        count = 0
                        #$global img_count
                        img_count = 0
                        print "recording started"
                        video_check()

                if count == 15:
                        print "splitting started"
                        
                        split_count += 1
                        recent_h264 = patient_vid_dir+"video"+str(split_count)+".h264"
                        camera.split_recording(recent_h264)
                       # thread.start_new_thread(convert_video, ("hi",))
                        count = 0
                        if cam_status == 1:
                                video_check()
                        
                          
                if count == 13:
                    if camera.recording:
                        cam_status = 0
                        camera.stop_recording()
                        GPIO.output(10,GPIO.LOW)
                        count = 0
       
                        
                    else:
                        count = 0
                        print "recording already stopped"
                if count == 14:
                    if camera.recording:
                        #global img_count
                        img_count = img_count + 1
                        #global patient_img_dir
                        camera.capture(patient_img_dir+"Image"+str(img_count)+'.jpg')
                        count = 0
                        print "snap taken"
                    else:
                        count = 0
                        "Start recording the vodeo then take snapshot"
		try:
	                stream.seek(0)
        	        cls.frame = stream.read()

                	# reset stream for next frame
	                stream.seek(0)
        	        stream.truncate()
		except OSError:
			print "Broken PIPE error"

                # if there hasn't been any clients asking for frames in
                # the last 10 seconds stop the thread
                if time.time() - cls.last_access > 10:
                    break
         cls.thread = None
        except:
         print "No Input signal"

class PDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Calculate width of title and position
        w = self.get_string_width(title)+15
        self.set_x((210 - w) / 2)
        # Colors of frame, background and text
        self.set_draw_color(0, 80, 180)
        self.set_fill_color(230, 230, 0)
        self.set_text_color(220, 50, 50)
        # Thickness of frame (1 mm)
        self.set_line_width(1)
        # Title
        self.cell(w, 9, title, 1, 1, 'C', 1)
        fd = open("doc1.txt", 'r+')
        self.set_font('Times', '', 10)
        txt = fd.read()
        txt = txt.split('___')
        fd.close()
        
        self.cell(150)
        self.cell(30,10,txt[18],0,1)
        self.cell(150)
        self.cell(30,15,txt[17])
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-25)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Text color in gray
        self.set_text_color(128)
        self.cell(150)
        self.cell(0, 5,'Doctor sign')
        self.ln(10)


        
        #self.cell(140)
        self.line(10, 280, 180, 280)
        self.set_font('Arial', 'I', 9)
        self.cell(0, 5,'24/1 Keshava plaza rajajinagar 1st main 20th cross bangalore-560010')
        # Thickness of frame (1 mm)
        #pdf.set_line_width(1)

    def chapter_title(self, num, label):
        # Arial 12
        self.set_font('Arial', '', 12)
        # Background color
        self.set_fill_color(200, 220, 255)
        # Title
        self.cell(0, 6, '%s' % (label), 0, 1, 'L', 1)
        # Line break
        self.ln(4)

    def chapter_body(self, name):
        # Read text file
        fd = open("doc1.txt", 'r+')
        self.set_font('Times', '', 12)
        txt = fd.read()

        fd.close()
        #print txt
        txt = txt.split('___')
        print txt

        #print txt[8]
        #print txt[9]
        #print txt[11]
        #print txt[10]
        #print txt[12]
        #print txt[15]
        #print txt[16]
        #print txt[6]
        #print txt[7]
        self.text(20,50,"ID                 :-"+txt[12])
        self.text(100,50,"Surgion :-"+txt[9])
        self.text(20,60,"Name            :-"+txt[13])
        self.text(20,70,"Gender          :-"+txt[15])
        self.text(20,80,"Age               :-"+txt[14])
        self.text(20,90,"DOB             :-"+txt[16])
        self.text(20,100,"Contact No   :-"+txt[19])
        self.text(20,110,"Address        :-"+txt[20])
        self.text(20,120,"Procedure Performed   :-"+txt[10])

        self.text(20,130,"Description   :-"+txt[11])

        

        #self.ln(1)
        # Times 12
        
        # Output justified text
        
     

    def print_chapter(self, num, title, name):
        self.add_page()
        self.chapter_title(num, title)
        self.chapter_body(name)


@app.route('/data')
def hello():
    try:
        ch = request.args['patient_id']
        #print ch
        chk_dir = "/media/pi/internal/"+ch
        out = os.path.exists(chk_dir)

        if out == True:

            fd = open(chk_dir+"/Docs/"+"patient_info.txt", 'r+')
            txt = fd.read()
            fd.close()
            txt = txt.replace(' ','')
            txt = txt.split('\n')

            #print txt[3]
            return "~present!"+txt[1]+txt[3]+txt[7]+txt[5]+txt[9]+txt[17]+txt[15]+txt[11]+txt[13]+"*"
        else:
            return "Not Found"
    except:
        print "Error in data?patient_id=RCT01"


        
@app.route("/report")
def report():
    if 'parameters' in request.args:
	 dat = request.args['parameters']
	 fd = open("doc1.txt", 'rw+')
    	 fd.write(dat)
         img = dat.split('___')
         fd.close()
         print img[0]
         print img[1]
         print img[2]
         print img[3]
         print img[4]
         print img[5]
         print img[6]
         print img[7]


         print img[8]
         print img[9]
         print img[10]
         print img[11]
         print img[12]
         print img[13]
         print img[14]
         print img[15]
         print img[16]
         print img[17]
         print img[18]
         print img[19]
         print img[20]
         print img[21]
         print img[22]

         pdf = PDF()
         global title
         title = img[21]+"     "
      
         pdf.set_title(title)
         pdf.set_author('Sharan Sulibhavi')
         pdf.print_chapter(1, "Operation: "+img[8], 'doc1.txt')
         
         image1 = [img[0],img[1],img[2],img[3],img[4],img[5],img[6],img[7]]
         x = [40,140,100,140,40,200,100,200,40,140,100,140,40,200,100,200]
         j = 0
         k = 0
         for i in range(4):
            if image1[j] == "NULL":
                pass
            else:
                pdf.image(image1[j], x[k],x[k+1], 50, 50)
                #self.image('1.jpg', 40,140, 50, 50)
                if k == 0:
                    pdf.text(40,195,"fig1: "+image1[j+1])
                #self.image('2.jpg', 100,140, 50, 50)
                elif k == 2:
                    pdf.text(100,195,"fig2: "+image1[j+1])
                #self.image('3.jpg', 40,200, 50, 50)
                elif k == 4:
                    pdf.text(40,255,"fig3: "+image1[j+1])
                #self.image('4.jpg', 100,200, 50, 50)
                elif k == 6:
                    pdf.text(100,255,"fig4: "+image1[j+1])
                k = k+2
            j = j+2
            
         global storage
         #/media/pi/internal/Id=hhh/Docs
         pnt = storage+img[12]+'/Docs/'
         #print pnt
	 pdf.output(pnt+'report.pdf', 'F')
 
    return 'Success'



@app.route('/MemSelection')
def Mem():
    try:
       global storage
       global add
       ch = request.args['option']
       if ch == "internal":          
            sel = "int"

       elif ch == "external":            
            sel = "ext"
         
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
           #print 'no extenal memory'
           found = 0
           
       else:
           #print "external device is at: ",usb_list[0]
           global add
           add = usb_list[0]
           found = 1

       
       if sel == "int":
           output = subprocess.Popen(int_card,stdout=subprocess.PIPE,shell=True)
           out = output.communicate()[0].replace("  "," ")
           out = out.replace("  "," ")
           out = out.replace("  ","")
           out = out.split(' ')
#           sec = float(out[7])/1900 #114MB/Min recordding rate(114/60 = 1.9MBPS)
           sec = float(out[7])/2417 #145MB/Min recordding rate(145/60 = 2.417MBPS)
           chk = float(out[7])/1024
           if chk <=100.00:
                return "very less memory"
           mem = float(out[7])/1024/1024
           mem = round(mem,2)
           sec = float(sec)
           if sec >= 3600.00:
                     hr = sec/3600
                     mn = (hr - int(hr))*60
                     hr = int(hr)
                     mn = int(mn)
           else:
                    mn = sec/60
                    hr = 0
                    mn = int(mn)
           global storage
           storage = "/media/pi/internal/"
       
           return "S"+str(hr)+'Hour(s)'+','+str(mn)+'Minute(s)'+"free:"+str(mem)+"GB""fr"
           
       elif sel == "ext":
             if found == 0:
                
                 storage = "not_connect"
                 return "no external memory"
             else:                
                 output = subprocess.Popen(ext_card,stdout=subprocess.PIPE,shell=True)
                 out = output.communicate()[0].replace("  "," ")
                 out = out.replace("  "," ")
                 out = out.replace("  ","")
                 out = out.split(' ')
                 sec = float(out[7])/1900
                 chk = float(out[7])/1024
                 if chk <= 100.00:
                     return "very less memory" 
                 mem = float(out[7])/1024/1024
                 mem = round(mem,2)
                 sec = float(sec)
                 if sec >= 3600.00:
                     hr = sec/3600
                     mn = (hr - int(hr))*60
                     hr = int(hr)
                     mn = int(mn)
                 else:
                    mn = sec/60
                    hr = 0
                    mn = int(mn)
                   
                    
                 storage = add+'/'
                 #print "testing:",storage + '----'+add
                 return "S"+str(hr)+'Hour(s)'+','+str(mn)+'Minute(s)'+"free:"+str(mem)+"GB""fr"
    except:
        print "Error in memory selection"

@app.route('/video')
def video():   

           dat = request.args['parameters']

           #print "Sent data",dat
           #removing \ in recieved test
           dat = dat.replace("\"","")

           if not regex.search(dat):
              return "Special characters error"

           #dat = dat.replace("^^"," ")
           #splitting the text if , found in text
           dat = dat.split('___')
           #print "Sent data",dat
                         
	   cmd = 'sudo mkdir '
	   global storage
	   if storage == "not_connect":
              return "no external memory"
	   #print storage
	   chk_dir = storage+dat[0]
	   cmd = cmd+chk_dir
           try:
               out = os.path.exists(chk_dir)
           except:
               return "check error"
           if out == True:
               return "directory exist"
           else:

              try:
                output = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
                out = output.communicate()
                dir1 = dat[0]
                cmd = 'sudo mkdir '+storage+dir1+'/Snap'
                global patient_img_dir
                patient_img_dir = storage+dir1+'/Snap/'
                output = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
                out = output.communicate()
                cmd = 'sudo mkdir '+storage+dir1+'/videos'
                global patient_vid_dir
                patient_vid_dir = storage+dir1+'/videos/'
                output = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
                out = output.communicate()
                cmd = 'sudo mkdir '+storage+dir1+'/Docs'
                output = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
                out = output.communicate()
                  #open the file to store patient data
                target = open(storage+'/'+dir1+'/Docs/patient_info.txt','w')
                target.truncate()
                target.write("=======Patient details===========")
                target.write("\n")	
                for d in dat:
		    wd = d.replace("-","-")
		    target.write(wd)
		    target.write("\n")
		    target.write("\n")
                target.write("=============EOF====================")
              except:
                return "patient info/directory not created"
           return "data created"


@app.route("/project")
def project():
      ch = request.args['option']
      global count
      if ch == "start":
           count = 12
           while(count == 12):
               status = 'started video'
            


      elif ch == "snapshot":
           count = 14
           while(count == 14):
               status = "snapshot taken"

      elif ch == "stop":
           count = 13
           while(count == 13):
               status = 'camera stopped'

               
	   
      return status

       
def shutdown(channel):
    global time_stamp

    time_now = time.time()
    if (time_now - time_stamp) >= 1.5:
        try:
            #write here for poweroff
            print "powered off"
            GPIO.output(11,GPIO.LOW)
        except:
            print "Error Occured" 
    time_stamp = time_now            

       
def play_pause(channel):
    global time_stamp

    time_now = time.time()
    if (time_now - time_stamp) >= 1.0:
        try:
            #write here for play/pause code
            print "pressed play/pause button"
        except:
            print "Error Occured" 
    time_stamp = time_now            


def disk_check():
    path = "/"
    dc = threading.Timer(5.0,disk_check)
    dc.start()
    st = os.statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    chk = round(float(free)/1024/1024,2)
    
    print chk
    if chk <=100.00:
        global count
        count = 13
        dc.cancel()
        print "Disk full and camera stopped recording"


def video_check():
    global split_count
    global patient_vid_dir
    global one
    global count
    global cam_status
    vc = threading.Timer(4.0,video_check)
    vc.start()


    fil = patient_vid_dir+"video"+str(split_count)+".h264"
    out = subprocess.Popen("du -s "+fil, stdout=subprocess.PIPE, shell=True)
    py=out.communicate()[0]
    size = int(py.split('\t')[0])
            
           
    print "size of video file",split_count,size
    if cam_status == 0:
            vc.cancel()
            print "video check stopped"
            chk =  "sudo find "+patient_vid_dir +" -name " + "\"" + "*.h264" + "\""

            out = subprocess.Popen(chk, stdout=subprocess.PIPE, shell=True)
            py=out.communicate()[0]
            py = py.rstrip('\n')
            thread.start_new_thread(stop_convert_video, (py,))
            
   
    if size >= 100000:
        print "video crossed 10MB"
        vc.cancel()
        count = 15
        thread.start_new_thread(convert_video, ("hi",))
        sleep(5)
            
        
def takesnap(channel):
    global time_stamp       # put in to debounce
    global count
    time_now = time.time()
    if (time_now - time_stamp) >= 1.5:
        if camera.recording():
            count = 14
    time_stamp = time_now
    




@app.route('/host_live')
def index():
    """Video streaming home page."""
    return render_template('stream.html')



def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def handler(s,p):
        print "Catch Broken PIPE"
        print "Error no is",s,p

if __name__ == "__main__":
        #disk_check()
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Snapshot key
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  #power off
        GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  #play-pause
        GPIO.setup(22, GPIO.OUT)    #standby
        GPIO.setup(10, GPIO.OUT)    #Recording
        GPIO.setup(9, GPIO.OUT)     #Online
        GPIO.setup(11, GPIO.OUT)    #Poweron
        GPIO.setup(5, GPIO.OUT)     #Diskfull alert 
        time_stamp = time.time()
        GPIO.add_event_detect(17, GPIO.RISING, callback=takesnap)
        GPIO.add_event_detect(4, GPIO.RISING, callback=shutdown)
        GPIO.add_event_detect(27, GPIO.RISING, callback=play_pause)
        GPIO.output(11,GPIO.HIGH)
        GPIO.output(5,GPIO.LOW)     
        count = 0
	signal(SIGPIPE,handler)
        img_count = 0      
        app.run(host='0.0.0.0',port=5000,debug=True,threaded=True)

