# EECSE4764 Lab4 Check3
# Group 6: NetSpeed Fast
# Group members: Ruochen You (ry2349), Penghe Zhang (pz2244), Linnan Li(ll3235)
# Date: 10/9/2018


import machine
import ssd1306
import urequests
import network
import time
from machine import Pin

i2c = machine.I2C(-1, Pin(5), Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
msg_list = ["Hello", "world", "Lab4"]
msg_idx = 0
msg_sent = False


def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('Columbia University', '')
        while not sta_if.isconnected():
            pass
    return sta_if.ifconfig()


def change(p):
    global msg_idx, msg_list
    # debounce
    irq_state = machine.disable_irq()
    active = 0
    while active < 20:
        if p.value() == 0:
            active += 1
        else:
            return
        time.sleep_ms(1)

    oled.fill(0)
    msg_idx = (msg_idx + 1) % 3
    oled.text(msg_list[msg_idx], 0, 0)
    oled.show()
    print(msg_list[msg_idx])
    time.sleep(0.5)
    machine.enable_irq(irq_state)


def send(p):
    global msg_sent
    # debounce
    irq_state = machine.disable_irq()
    active = 0
    while active < 20:
        if p.value() == 0:
            active += 1
        else:
            return
        time.sleep_ms(1)

    msg_sent = True
    machine.enable_irq(irq_state)


def main():
    global msg_sent
    # button_b is to change message; button_c is to send twitter
    button_c = Pin(2, Pin.IN, Pin.PULL_UP)
    button_b = Pin(12, Pin.IN, Pin.PULL_UP)
    button_c.irq(trigger=Pin.IRQ_FALLING, handler=send)
    button_b.irq(trigger=Pin.IRQ_FALLING, handler=change)

    do_connect()

    while True:
        oled.fill(0)
        oled.text("send twitter", 0, 0)
        oled.show()

        if msg_sent:
            url = "https://api.thingspeak.com/apps/thingtweet/1/statuses/update?api_key=%s&status=%s" % \
                  ("1BP40VDZLGYUQKSS", msg_list[msg_idx])
            r = urequests.post(url)
            print(r.text)
            oled.fill(0)
            oled.text("twitter sent", 0, 0)
            oled.show()
            time.sleep(0.5)
            msg_sent = False


if __name__ == '__main__':
    main()

