# EECSE4764 Lab1 Check2
# Group 6: NetSpeed Fast
# Group members: Ruochen You (ry2349), Penghe Zhang (pz2244), Linnan Li(ll3235)
# Date: 9/12/2018

from machine import Pin
import time

def blink(step, *p):
    for i in p:
        i.value(0)
    time.sleep(step)
    
    for i in p:
        i.value(1)
    time.sleep(step)

def sep_loop(led1, led2):
    # led1 will blink every 100ms & led2 will blink every 500ms
    for i in range(5):
        if i != 4:
            blink(0.1, led1)
        else:
            blink(0.1, led1, led2)

def main():
    led1 = Pin(0, Pin.OUT)
    led2 = Pin(2, Pin.OUT)
    # init the leds
    led1.value(1)
    led2.value(1)

    while True:
        sep_loop(led1, led2)

if __name__ == '__main__':
    main()