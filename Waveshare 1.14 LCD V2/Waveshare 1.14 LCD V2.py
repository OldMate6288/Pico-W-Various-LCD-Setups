import network
import socket
import framebuf
import time
import urequests
from machine import Pin,SPI,PWM
from time import sleep
n = 0
led = Pin('LED', Pin.OUT)

# LCD PINS
BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

# BUTTON PINS (UNUSED FOR NOW)
keyA = Pin(15,Pin.IN,Pin.PULL_UP)
keyB = Pin(17,Pin.IN,Pin.PULL_UP)
key2 = Pin(2 ,Pin.IN,Pin.PULL_UP)
key3 = Pin(3 ,Pin.IN,Pin.PULL_UP)
key4 = Pin(16 ,Pin.IN,Pin.PULL_UP)
key5 = Pin(18 ,Pin.IN,Pin.PULL_UP)
key6 = Pin(20 ,Pin.IN,Pin.PULL_UP)

# LCD 1.14 Version 2
class LCD_1inch14(framebuf.FrameBuffer):
    def __init__(self):
        self.temp = bytearray(1)
        self.width = 240
        self.height = 135
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)
        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,65_000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()
        self.red   =   0x07E0
        self.green =   0x001f
        self.blue  =   0xf800
        self.white =   0xffff
        self.yellow=   0xFFE0
        self.orange=   0xE0FC
        self.black =   0x0

    def write_cmd(self, cmd):
        self.temp[0] = cmd
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(self.temp)
        self.cs(1)

    def write_data(self, buf):
        self.temp[0] = buf
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.temp)
        self.cs(1)

    def init_display(self):
        # Initialize dispaly 
        self.rst(1)
        self.rst(0)
        self.rst(1)
        self.write_cmd(0x36)
        self.write_data(0x70)
        self.write_cmd(0x3A) 
        self.write_data(0x05)
        self.write_cmd(0xB2)
        self.write_data(0x0C)
        self.write_data(0x0C)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)
        self.write_cmd(0xB7)
        self.write_data(0x35) 
        self.write_cmd(0xBB)
        self.write_data(0x19)
        self.write_cmd(0xC0)
        self.write_data(0x2C)
        self.write_cmd(0xC2)
        self.write_data(0x01)
        self.write_cmd(0xC3)
        self.write_data(0x12)   
        self.write_cmd(0xC4)
        self.write_data(0x20)
        self.write_cmd(0xC6)
        self.write_data(0x0F) 
        self.write_cmd(0xD0)
        self.write_data(0xA4)
        self.write_data(0xA1)
        self.write_cmd(0xE0)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0D)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2B)
        self.write_data(0x3F)
        self.write_data(0x54)
        self.write_data(0x4C)
        self.write_data(0x18)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x1F)
        self.write_data(0x23)
        self.write_cmd(0xE1)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0C)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2C)
        self.write_data(0x3F)
        self.write_data(0x44)
        self.write_data(0x51)
        self.write_data(0x2F)
        self.write_data(0x1F)
        self.write_data(0x1F)
        self.write_data(0x20)
        self.write_data(0x23)
        self.write_cmd(0x21)
        self.write_cmd(0x11)
        self.write_cmd(0x29)

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x28)
        self.write_data(0x01)
        self.write_data(0x17)
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x35)
        self.write_data(0x00)
        self.write_data(0xBB)
        self.write_cmd(0x2C)
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)

if __name__=='__main__':
    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(32768)# max 65535
    LCD = LCD_1inch14()
    
    # Change to your router settings
    ssid = 'SSID'
password = 'PASSWORD'

# Webserver
html = """<!DOCTYPE html>
<html>
    <head>
    <style>
        h1 {text-align: center;}
        p {text-align: center;}
        div {text-align: center;}
    </style>
    <title>Pico W LCD Test</title> </head>
    <body> <h1>ANDROID TEST STUFF</h1>
        <p>%s</p>
        <p><a href="intent://com.android.settings/#Intent;scheme=android-app;end">OPEN SETTINGS</a></p>
        <p><a href="intent://com.sec.android.app.myfiles/#Intent;scheme=android-app;end">OPEN MY FILES</a></p>
        <p><a href="https://apkcombo.com/alliance-shield-app-manager/com.rrivenllc.shieldx/download/apk">DOWNLOAD ALLIANCE SHIELD</a></p>
        <p><a href="intent://com.rrivenllc.shieldx/#Intent;scheme=android-app;end">OPEN ALLIANCE SHIELD</a></p>
    </body>
</html>
"""

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

connectCount = 0

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 10:
        break
    max_wait -= 1
    LCD.fill(LCD.black)
    LCD.text("waiting for connection...", 1, 1,LCD.white)
    LCD.show()
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    LCD.fill(0)
    LCD.text("network connection failed", 1, 1,LCD.white)
    LCD.show()
    raise RuntimeError('network connection failed')
else:
    led.toggle()
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

# Get current time
r = urequests.get('http://worldtimeapi.org/api/ip')
result = str(r.content)
startTime = result[int(result.find("datetime")) + 11:30 + result.find("datetime")]

LCD.fill(LCD.black)
LCD.show()
LCD.text("Start Time:", 1, 1,LCD.white)
LCD.text(startTime, 1, 11,LCD.white)
LCD.text("IP Address:", 1, 21,LCD.white)
LCD.text(str(status[0]), 1, 31,LCD.white)
LCD.show()


print('Start Time', startTime)
print('listening on', addr)

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        clientIP = addr[0]
        print('client connected from', clientIP)
        request = cl.recv(1024)
        
        LCD.fill(0)
        LCD.text("Start Time:", 1, 1,LCD.white)
        LCD.text(startTime, 1, 11,LCD.white)
        LCD.text("IP Address:", 1, 21,LCD.white)
        LCD.text(str(status[0]), 1, 31,LCD.white)
        LCD.text("Last Client IP:", 1, 41,LCD.white)
        LCD.text(clientIP, 1, 51,LCD.white)
        LCD.show()
        
        request = str(request)
        connectCount += 1
        countText = "This site has been accessed " + str(connectCount) + " time since " + startTime

        response = html % countText

        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()

    except OSError as e:
        cl.close()
        print('connection closed')
