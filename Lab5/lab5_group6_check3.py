# EECSE4764 Lab5 Check3
# Group 6: NetSpeed Fast
# Group members: Ruochen You (ry2349), Penghe Zhang (pz2244), Linnan Li(ll3235)
# Date: 10/16/2018


import network
import machine
import ssd1306
import socket
import time
from machine import Pin

i2c = machine.I2C(-1, Pin(5), Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
led = Pin(0, Pin.OUT)
led.value(1)
oled_on = False


def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('Columbia University', '')
        while not sta_if.isconnected():
            pass
    return sta_if.ifconfig()


ip_addr = do_connect()
print(ip_addr)

socket_addr = socket.getaddrinfo(ip_addr[0], 80)[0][-1]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(socket_addr)
s.listen(1)
print('listening on', socket_addr)

while True:
    cl, addr = s.accept()
    print('client connected from', addr)
    request = cl.recv(1024)
    request = str(request)
    print('content = %s' % request)

    if 'msg' in request:
        msg = request.split('/?msg=')[1].split('HTTP')[0]
        msg = msg.replace('%20', ' ')

        resp_msg = msg
        # some specific vocal message
        # led
        if 'start' in msg:
            led.value(0)
            resp_msg = "start the led now"
        elif 'stop' in msg:
            led.value(1)
            resp_msg = "stop the led now"
        # oled
        elif 'on' in msg:
            oled_on = True
            resp_msg = "turn on the oled now"
        elif 'off' in msg:
            oled_on = False
            resp_msg = "turn off the oled now"
            oled.fill(0)
            oled.show()
        # just for fun ...
        elif msg == 'frog':
            msg = "You are not a magician! -1s"

        if oled_on:
            oled.fill(0)
            oled.text(msg, 0, 0)
            oled.show()

        suc_response = "HTTP/1.1 200 OK\r\n\r\n%s" % resp_msg
        cl.send(str.encode(suc_response))

    else:
        fail_response = "HTTP/1.1 501 Implemented\r\n\r\nPlease attach msg!"
        cl.send(str.encode(fail_response))

    time.sleep(1)
    cl.close()


