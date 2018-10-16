# EECSE4764 Lab3 Check2
# Group 6: NetSpeed Fast
# Group members: Ruochen You (ry2349), Penghe Zhang (pz2244), Linnan Li(ll3235)
# Date: 10/2/2018


import time, machine, ssd1306
from machine import Pin

rtc = machine.RTC()
rtc.datetime((2018, 1, 1, 0, 0, 0, 0, 0))

i2c = machine.I2C(-1, Pin(5), Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
adc = machine.ADC(0)
cur = 0
pos = [6, 5, 4, 2, 1, 0]
pos_name = ["second", "minute", "hour", "day", "month", "year"]


# display time on the oled
def display_time():
    oled.fill(0)
    cur_date = "date: " + str(rtc.datetime()[0]) + '/' + str(rtc.datetime()[1]) + '/' + str(rtc.datetime()[2])
    cur_time = "time: " + str(rtc.datetime()[4]) + ':' + str(rtc.datetime()[5]) + ':' + str(rtc.datetime()[6])
    oled.text(cur_date, 0, 0)
    oled.text(cur_time, 0, 10)
    oled.show()


# change which pos do you want to change
def change_pos(p):
    global cur, pos_name
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
    cur = (cur + 1) % 6
    oled.text(pos_name[cur], 0, 0)
    oled.show()

    machine.enable_irq(irq_state)


# plus 1 on the position
def acc_time(p):
    global cur, rtc
    # debounce
    irq_state = machine.disable_irq()
    active = 0
    while active < 20:
        if p.value() == 0:
            active += 1
        else:
            return
        time.sleep_ms(1)

    cur_datetime = list(rtc.datetime())
    cur_datetime[pos[cur]] += 1
    rtc.datetime(tuple(cur_datetime))

    machine.enable_irq(irq_state)


def main():
    button_b = Pin(12, Pin.IN, Pin.PULL_UP)
    button_c = Pin(2, Pin.IN, Pin.PULL_UP)

    button_b.irq(trigger=Pin.IRQ_FALLING, handler=change_pos)
    button_c.irq(trigger=Pin.IRQ_FALLING, handler=acc_time)

    while True:
        display_time()
        oled.contrast(adc.read())
        time.sleep(1)


if __name__ == '__main__':
    main()
