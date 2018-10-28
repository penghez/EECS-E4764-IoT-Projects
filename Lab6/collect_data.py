import network
import machine
import ssd1306
import usocket
import ustruct
import gc
from machine import Pin
import time

i2c = machine.I2C(-1, Pin(5), Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
spi = machine.SPI(-1, baudrate=500000, polarity=1, phase=1, sck=Pin(0), mosi=Pin(16), miso=Pin(2))
cs = Pin(15, Pin.OUT)
record_state = -1
team_no = 1
button_b = Pin(12, Pin.IN)


def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('Columbia University', '')
        while not sta_if.isconnected():
            pass
    return sta_if.ifconfig()


def get_pos():
    reg = 0x80 | 0x32 | 0x40
    write_reg_val = ustruct.pack('B', reg)

    x1 = bytearray(1)
    x2 = bytearray(1)
    y1 = bytearray(1)
    y2 = bytearray(1)
    z1 = bytearray(1)
    z2 = bytearray(1)

    cs.value(0)
    spi.write(write_reg_val)
    spi.readinto(x1)
    spi.readinto(x2)
    spi.readinto(y1)
    spi.readinto(y2)
    spi.readinto(z1)
    spi.readinto(z2)
    cs.value(1)

    x = (ustruct.unpack('b', x2)[0] << 8) | ustruct.unpack('b', x1)[0]
    y = (ustruct.unpack('b', y2)[0] << 8) | ustruct.unpack('b', y1)[0]
    z = (ustruct.unpack('b', z2)[0] << 8) | ustruct.unpack('b', z1)[0]
    print(x, y, z)
    return x, y, z


def record(p):
    # debounce
    global record_state
    irq_state = machine.disable_irq()
    active = 0
    while active < 20:
        if p.value() == 0:
            active += 1
        else:
            return
        time.sleep_ms(1)

    if record_state == -1:
        record_state = 1
    else:
        record_state = 1 - record_state

    machine.enable_irq(irq_state)


def write(register, value):
    write_val = ustruct.pack('B', value)
    write_reg_val = ustruct.pack('B', register)

    cs.value(0)
    spi.write(write_reg_val)
    spi.write(write_val)
    cs.value(1)


def reallocate():
    # free the memory
    gc.collect()
    gc.mem_free()
    button_b.irq(trigger=Pin.IRQ_FALLING, handler=record)


def generate_clean_list(letters):
    if len(letters) < 20:
        return []
    else:
        new_list = []
        a = len(letters) // 20
        b = len(letters) % 20
        idx = 0
        for i in range(20):
            tempx = 0
            tempy = 0
            for j in range(a):
                tempx += letters[idx + j][0]
                tempy += letters[idx + j][1]
            tempx = tempx // a
            tempy = tempy // a
            new_list.append([tempx, tempy])
            idx += a
            if b > 0:
                idx += 1
                b -= 1
        return new_list


do_connect()
# data format
write(0x31, 0x01)
# power ctl
write(0x2D, 0x08)
button_b.irq(trigger=Pin.IRQ_FALLING, handler=record)

letter_list = []

while True:
    if record_state == 1:
        x, y, _ = get_pos()

        # url = "http://52.90.217.13/post"
        # _, _, host, path = url.split('/', 3)
        # addr = usocket.getaddrinfo(host, 8080)[0][-1]
        #
        # print(start)
        # s = usocket.socket()
        # s.connect(addr)
        # post_json = '{"xcoordinate": ' + str(x) + ', "ycoordinate": ' + str(y) + ', "zcoordinate": ' + str(start) + '}'
        # post = 'POST /%s HTTP/1.1\r\nContent-length: %d\r\nContent-Type: application/json\r\nHost: %s\r\n\r\n%s' % \
        #        (path, len(post_json), host, post_json)
        #
        # s.send(str.encode(post))
        # reallocate()
        letter_list.append([x, y])
        time.sleep(0.05)

    if record_state == 0:
        send_list = generate_clean_list(letter_list)
        if len(send_list) < 20:
            continue
        else:
            print("start sending message for team %d......" % team_no)
            for i in range(20):
                cx = send_list[i][0]
                cy = send_list[i][1]

                url = "http://52.90.217.13/post"
                _, _, host, path = url.split('/', 3)
                addr = usocket.getaddrinfo(host, 8080)[0][-1]

                print("The %dth coordinates:" % i)
                s = usocket.socket()
                s.connect(addr)
                post_json = '{"xcoordinate": ' + str(cx) + ', "ycoordinate": ' + str(cy) + ', "zcoordinate": ' + str(team_no) + '}'
                post = 'POST /%s HTTP/1.1\r\nContent-length: %d\r\nContent-Type: application/json\r\nHost: %s\r\n\r\n%s' % \
                       (path, len(post_json), host, post_json)

                s.send(str.encode(post))
                print(cx, cy)
                reallocate()
                time.sleep(0.2)

            record_state = -1
            letter_list = []

            print("%dth team sent complete!" % team_no)
            team_no += 1

