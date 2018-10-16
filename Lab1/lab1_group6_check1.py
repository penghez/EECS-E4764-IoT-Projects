# EECSE4764 Lab1 Check1
# Group 6: NetSpeed Fast
# Group members: Ruochen You (ry2349), Penghe Zhang (pz2244), Linnan Li (ll3235)
# Date: 9/12/2018

from machine import Pin
import time

def blink(step, p):
    p.value(0)
    time.sleep(step)
    p.value(1)
    time.sleep(step)

# SOS: three quickly - three slowly - three quickly - pause
def SOS_loop(led):
    for i in range(3):
        if i != 1:
            # blink quickly
            for j in range(3):
                blink(0.2, led)
        else:
            # blink slowly
            for j in range(3):
                blink(0.5, led)

    # pause between two SOS signals
    time.sleep(0.5)

def main():
    led = Pin(0, Pin.OUT)
    # init the led
    led.value(1)

    while True:
        SOS_loop(led)
        
if __name__ == '__main__':
    main()
