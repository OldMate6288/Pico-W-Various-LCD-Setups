from wificfg import ssid,password
import network
import socket
import time
import utime
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
n = 0
led = Pin('LED', Pin.OUT)

WIDTH  = 128                                            # oled display width
HEIGHT = 32                                             # oled display height

# I2C0 pin assignments
SCL = 5
SDA = 4

# Initialize I2C0, Scan and Debug print of SSD1306 I2C device address
i2c = I2C(0, scl=Pin(SCL), sda=Pin(SDA), freq=200000)
print("Device Address      : "+hex(i2c.scan()[0]).upper())

oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)                  # Init oled display


ssid = ssid
password = password

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

connectCount = 0

# Webserver
html = """<!DOCTYPE html>
<html>
    <head>
    <style>
        h1 {text-align: center;}
        p {text-align: center;}
        div {text-align: center;}
    </style>
    
    <title>PICO WEBSERVER</title> </head>
    
    <body background="PASTE IMAGE/GIF LINK HERE OR CHANGE COLOUR VALUE">
    
        <h1><p style = "font-family:monospace;font-size:32px;font-style:normal;color:#00FF00;">PICO WEBSERVER</p></h1>
        
        <p><p style = "font-family:monospace;font-size:16px;font-style:normal;color:#00FF00;">%s</p>
        
        <p><form action="https://soundcloud.com/search?q=" class="searchform" method="get" name="searchform" target="_blank"></p>
        <input name="sitesearch" type="hidden">
        <p><input autocomplete="on" class="form-control search" name="q" placeholder="Search" required="required"  type="text"></p>
        <p><button class="button" type="submit">Search SoundCloud</button></p>
        </form>
        
        <p><form action="https://www.google.com/search" class="searchform" method="get" name="searchform" target="_blank"></p>
        <input name="sitesearch" type="hidden">
        <p><input autocomplete="on" class="form-control search" name="q" placeholder="Search" required="required"  type="text"></p>
        <p><button class="button" type="submit">Search Google</button></p>
        </form>
        
        <h1><p style = "font-family:monospace;font-size:32px;font-style:normal;color:#00FF00;">ANDROID STUFF</p></h1>
        
        <p><a href="intent://com.android.settings/#Intent;scheme=android-app;end">OPEN SETTINGS</a></p>
        <p><a href="intent://com.sec.android.app.myfiles/#Intent;scheme=android-app;end">OPEN MY FILES</a></p>
        <p><a href="https://apkcombo.com/alliance-shield-app-manager/com.rrivenllc.shieldx/download/apk">DOWNLOAD ALLIANCE SHIELD</a></p>
        <p><a href="intent://com.rrivenllc.shieldx/#Intent;scheme=android-app;end">OPEN ALLIANCE SHIELD</a></p>

    </body>
</html>
"""

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    oled.fill
    oled.text("Waiting for", 1, 1)
    oled.text("connection...", 1, 21)
    oled.show()
    print('waiting for connection...')
    # Was easier to do this manually, you can probably make this work alot better.
    led.toggle()
    led.toggle()
    led.toggle()
    led.toggle()
    led.toggle()
    led.toggle()
    led.toggle()
    led.toggle()
    led.toggle()
    led.toggle()
    time.sleep(1)

if wlan.status() != 3:
    oled.fill(0)
    oled.text("Connection", 1, 1)
    oled.text("failed", 1, 21)
    oled.show()
    raise RuntimeError('network connection failed')
else:
    led.toggle()
    oled.fill(0)
    oled.text("connected", 1, 1)
    oled.show()
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

# Get current time
import urequests
r = urequests.get('http://worldtimeapi.org/api/ip')
result = str(r.content)
startTime = result[int(result.find("datetime")) + 11:30 + result.find("datetime")]

print('Start Time', startTime)
print('listening on', addr)

# Listen for connections
while True:
    try:
        oled.fill(0)
        oled.text("Start Time:", 1, 1)
        oled.text(startTime, 1, 21)
        oled.show()
        utime.sleep(5)
    
        oled.fill(0)
        oled.text("IP Address:", 1, 1)
        oled.text(str(status[0]), 1, 21)
        oled.show()
        utime.sleep(5)

        cl, addr = s.accept()
        clientIP = addr[0]
        oled.fill(0)
        oled.text("Last Client IP:", 1, 1)
        oled.text(clientIP, 1, 21)
        oled.show()
        utime.sleep(5)
        print('client connected from', clientIP)
        request = cl.recv(1024)

        request = str(request)
        connectCount += 1
        countText = "This site has been accessed " + str(connectCount) + " times since " + startTime

        response = html % countText

        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()

    except OSError as e:
        cl.close()
        print('connection closed')