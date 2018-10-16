# EECSE4764 Lab2 Check3
# Group 6: NetSpeed Fast
# Group members: Ruochen You (ry2349), Penghe Zhang (pz2244), Linnan Li(ll3235)
# Date: 9/25/2018


import time
import machine
from machine import Pin


cur_state = 1


def callback(p):
    global cur_state

    active = 0
    cur_value = p.value()

    # debounce
    while active < 20:
        if p.value() == cur_value:
            active += 1
        else:
            active = 0
        time.sleep_ms(1)

    cur_state = 1 - cur_state


def main():
    switch = Pin(13, Pin.IN, Pin.PULL_UP)
    pwm = machine.PWM(Pin(15))
    adc = machine.ADC(0)
    pwm.freq(60)

    switch.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=callback)

    while True:
        if cur_state == 1:
            pwm.duty(1023)
        else:
            pwm.duty(adc.read())
            time.sleep_ms(100)


if __name__ == '__main__':
    main()

