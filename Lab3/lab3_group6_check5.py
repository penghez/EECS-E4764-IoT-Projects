# EECSE4764 Lab3 Check5
# Group 6: NetSpeed Fast
# Group members: Ruochen You (ry2349), Penghe Zhang (pz2244), Linnan Li(ll3235)
# Date: 10/2/2018


import machine
import ssd1306
import time

i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
spi = machine.SPI(1, baudrate=2000000, polarity=1, phase=1)
cs = machine.Pin(15, machine.Pin.OUT)


def get_pos():
    cs.value(0)
    x2 = spi.read(5, 0xf3)
    cs.value(1)

    cs.value(0)
    y2 = spi.read(5, 0xf5)
    cs.value(1)

    print("%s, %s" % (x2[1], y2[1]))
    return [x2[1], y2[1]]


def main():
    # initialize the power of ADXL345
    power_ctl = b'\x2d\x08'
    data_format = b'\x31\x0f'
    cs.value(0)
    spi.write(power_ctl)
    cs.value(1)
    cs.value(0)
    spi.write(data_format)
    cs.value(1)

    # init position of the word in oled
    px, py = 50, 10
    while True:
        oled.fill(0)
        oled.text('Group6', px, py)
        oled.show()

        avg_x = get_pos()[0]
        avg_y = get_pos()[1]

        if 0 < avg_x < 128:
            px += avg_x
        if avg_x > 128:
            px -= 256 - avg_x

        if 0 < avg_y < 128:
            py -= avg_y
        if avg_y > 128:
            py += 256 - avg_y

        if px >= 128:
            px = 0
        if px < 0:
            px = 128
        if py >= 32:
            py = 0
        if py < 0:
            py = 32

        time.sleep(0.001)


if __name__ == '__main__':
    main()
