'''
通过摄像头拍一张照片，然后识别出人是谁，进而控制门禁系统
@author: wanggangdan
@date:2018年12月10日
'''

from aip import AipFace
from picamera import PiCamera
import urllib.request
import RPi.GPIO as GPIO
import base64
import time
import pygame
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

#百度人脸识别API账号信息
APP_ID = '百度人脸识别的ID'
API_KEY = '百度人脸识别的KEY'
SECRET_KEY = '百度人脸识别的SECRET_KEY'
client = AipFace(APP_ID, API_KEY, SECRET_KEY)
#图像编码方式
IMAGE_TYPE='BASE64'
#用户组信息
GROUP = '自己创建用户组的名称'
camera = PiCamera()
pygame.mixer.init()
GPIO_IN_PIN = 15
GPIO_IN_PIN1 = 40
#定义一个摄像头对象
def getimage():
    camera.resolution = (1024,768)
    camera.start_preview()
    time.sleep(2)
    camera.capture('faceimage.jpg')
    pygame.mixer.music.load('/home/pi/voice/start.mp3')
    pygame.mixer.music.play()
    time.sleep(2)

#对图片的格式进行转换
def transimage():
    f = open('faceimage.jpg','rb')
    img = base64.b64encode(f.read())
    return img
#播放声音
def playvioce(name):
    pygame.mixer.music.load('/home/pi/voice/' +name)
    pygame.mixer.music.play()
#发送信息到微信上  
def sendmsg(name,main):
    url = "server酱生成的带key的网址"
    urllib.request.urlopen(url + "text="+name+"&desp="+main)
#发送信息到邮箱
def send():
    sender = '发送者的邮箱'
    receivers = '接受者的邮箱'
    password='发送的邮箱开启SMTP后生成的password'
    message =  MIMEMultipart('related')
    subject = '有陌生人来访！'
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = receivers
    content = MIMEText('<html><body><img src="cid:imageid" alt="imageid"></body></html>','html','utf-8')
    message.attach(content)

    file=open("faceimage.jpg", "rb")
    img_data = file.read()
    file.close()

    img = MIMEImage(img_data)
    img.add_header('Content-ID', 'imageid')
    message.attach(img)

    try:
        server=smtplib.SMTP_SSL("smtp.qq.com",465) #SMTP开启的邮箱和端口，笔者这里是qq邮箱的
        server.login(sender,password)
        server.sendmail(sender,receivers,message.as_string())
        server.quit()
        print ("邮件发送成功！")
    except smtplib.SMTPException:
        print('邮件发送失败！')
    
#上传到百度api进行人脸检测
def go_api(image):
    result = client.search(str(image, 'utf-8'), IMAGE_TYPE, GROUP);
    if result['error_msg'] == 'SUCCESS':
        name = result['result']['user_list'][0]['user_id']
        score = result['result']['user_list'][0]['score']
        if score > 80:
            print("Welcome %s !" % name)
            if name == 'xxxxxx':
                sendmsg("DoorOpen",name)
                playvioce('xxxxxx.mp3')
                time.sleep(5)
            if name == 'ssssss':
                sendmsg("DoorOpen",name)
                playvioce('ssssss.mp3')
                time.sleep(5)
                # playvioce('despacito.mp3')
                # time.sleep(5)
            if name == 'wanggangdan':
                sendmsg("DoorOpen",name)
                playvioce('wanggangdan.mp3')
                time.sleep(5)
        else:
            print("Sorry...I don't know you !")
            playvioce('noroot.mp3')
            send()
            name = 'Unknow'
            return 0
        # 将开门信息存在log.txt文档中
        curren_time = time.asctime(time.localtime(time.time()))
        f = open('Log.txt','a')
        f.write("Person: " + name + "     " + "Time:" + str(curren_time)+'\n')
        f.close()
        return 1
    if result['error_msg'] == 'pic not has face':
        print('There is no face in image!')
        playvioce('face.mp3')
        time.sleep(2)
        return 0
    else:
        print(result['error_code']+' ' + result['error_code'])
        return 0

#步进电机门锁控制
#开门
def motor_open():   
    steps    = 180;  
    clockwise = 1;  
  
    arr = [0,1,2,3];  
    if clockwise!=1:  
        arr = [3,2,1,0];  
  
    ports = [40,38,36,35] # GPIO 21（Pin 40） GPIO 20（Pin 38） GPIO 16（Pin 36） GPIO 19（Pin 35）  
  
    for p in ports:  
        GPIO.setup(p,GPIO.OUT)  
      
    for x in range(0,steps):  
        for j in arr:  
            time.sleep(0.002)  
            for i in range(0,4):  
                if i == j:              
                    GPIO.output(ports[i],True)  
                else:  
                    GPIO.output(ports[i],False)
#关门
def motor_close(): 
    steps    = 180;  
    clockwise = 0;  
  
    arr = [0,1,2,3];  
    if clockwise!=1:  
        arr = [3,2,1,0];  
  
    ports = [40,38,36,35] # GPIO 21（Pin 40） GPIO 20（Pin 38） GPIO 16（Pin 36） GPIO 19（Pin 35）  
  
    for p in ports:  
        GPIO.setup(p,GPIO.OUT)  
      
    for x in range(0,steps):  
        for j in arr:  
            time.sleep(0.002)  
            for i in range(0,4):  
                if i == j:              
                    GPIO.output(ports[i],True)  
                else:  
                    GPIO.output(ports[i],False)

#主函数
if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(GPIO_IN_PIN,GPIO.IN)
    GPIO.setup(GPIO_IN_PIN1,GPIO.IN)
    playvioce('waite.mp3')
    time.sleep(5)
    while True:
        time.sleep(0.5)
        print('等待检测')
        #if True:
        if GPIO.input(GPIO_IN_PIN) == GPIO.HIGH:
            getimage()
            img = transimage()
            res = go_api(img)
            if(res == 1):
                motor_open()
                time.sleep(1)
                motor_close()
            else:
                print('无法通过检测，请重试！')
            print('waite 5 seconds to do next')
            #playvioce('waite.mp3')
            #time.sleep(5)