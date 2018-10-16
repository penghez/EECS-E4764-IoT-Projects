# EECSE4764 Lab2 Check1
# Group 6: NetSpeed Fast
# Group members: Ruochen You (ry2349), Penghe Zhang (pz2244), Linnan Li(ll3235)
# Date: 9/25/2018


import time
import machine


def led_pwm(adc, pwm):
    pwm.freq(60)
    pwm.duty(adc.read())


def main():
    pwm = machine.PWM(machine.Pin(15))
    adc = machine.ADC(0)

    while True:
        led_pwm(adc, pwm)
        time.sleep_ms(100)


if __name__ == '__main__':
    main()
