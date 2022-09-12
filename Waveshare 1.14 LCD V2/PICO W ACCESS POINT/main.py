from machine import Pin, SoftSPI
from fonts import vga1_8x8 as font1
from fonts import vga1_16x32 as font2
import time
import socket
import network
import machine
import st7789 as st7789

ssid = 'Pico WiFi Test'
password = 'supersimplepw'

led = machine.Pin("LED",machine.Pin.OUT)

# Waveshare LCD 1.14 v2 Button Pins
keyA = Pin(15,Pin.IN,Pin.PULL_UP)
keyB = Pin(17,Pin.IN,Pin.PULL_UP)
key2 = Pin(2 ,Pin.IN,Pin.PULL_UP) # up
key3 = Pin(3 ,Pin.IN,Pin.PULL_UP) # ctrl
key4 = Pin(16 ,Pin.IN,Pin.PULL_UP) # left
key5 = Pin(18 ,Pin.IN,Pin.PULL_UP) # down
key6 = Pin(20 ,Pin.IN,Pin.PULL_UP) # right

LCD = st7789.ST7789(
    SoftSPI(baudrate=30000000, polarity=1, sck=Pin(10), mosi=Pin(11), miso=Pin(16)),
    135,
    240,
    reset=Pin(12, Pin.OUT),
    cs=Pin(9, Pin.OUT),
    dc=Pin(8, Pin.OUT),
    backlight=Pin(13, Pin.OUT),
    rotation=1)

LCD.fill(0x0000)
LCD.text(font2, "PICO W HOTSPOT", 9, 10, 0xF81F)
LCD.text(font1, "LOADING, PLEASE WAIT...", 31, 75, 0xFFFF)
LCD.text(font1, "Created By OldMate - 12/09/22", 5, 120, 0xFFE0)
time.sleep(3)

ap = network.WLAN(network.AP_IF)
ap.config(essid=ssid, password=password)
ap.active(True)

while ap.active() == False:
  pass

print('Connection successful')
print(ap.ifconfig())

html = """<!DOCTYPE html>
<html>
    <head> <title>Pico W</title> </head>
    <body> <h1>Pico W</h1>
        <p>Hello from Pico W.</p>
    </body>
</html>
"""

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)
wlan = network.WLAN(network.AP_IF)
status = wlan.ifconfig()
led.off()
LCD.fill(0x0000)
LCD.text(font1, "SSID:", 4, 15, 0xFFFF)
LCD.text(font1, str(ssid), 50, 15, 0x07E0)
LCD.text(font1, "PASSWORD:", 5, 35, 0xFFFF)
LCD.text(font1, str(password), 82, 35, 0x07E0)
LCD.text(font1, "IP Address:", 3, 55, 0xFFFF)
LCD.text(font1, str(status[0]), 96, 55, 0x07E0)
LCD.text(font1, "Listening On:", 5, 75, 0xFFFF)
LCD.text(font1, str(addr), 113, 75, 0x07E0)

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)
        request = cl.recv(1024)
        led.on()
        LCD.text(font1, "Client IP:", 5, 103, 0xFFFF)
        LCD.text(font1, str(addr), 4, 123, 0x07E0)
        print(request)

        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(html)
        cl.close()
        led.off()

    except OSError as e:
        cl.close()
        print('connection closed')