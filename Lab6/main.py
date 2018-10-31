# EECSE4764 Lab6
# Group 6: NetSpeed Fast
# Group members: Ruochen You (ry2349), Penghe Zhang (pz2244), Linnan Li(ll3235)
# Date: 10/31/2018

import network
import machine
import ssd1306
import usocket
import socket
import ustruct
import gc
from machine import Pin
import time

rtc = machine.RTC()
i2c = machine.I2C(-1, Pin(5), Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
spi = machine.SPI(-1, baudrate=500000, polarity=1, phase=1, sck=Pin(0), mosi=Pin(16), miso=Pin(2))
cs = Pin(15, Pin.OUT)
adc = machine.ADC(0)
record_state = -1
display = False
show_time_now = False
show_gesture = False
show_alarm = False
gesture_str = 'gesture'
button_b = Pin(12, Pin.IN)
button_c = Pin(14, Pin.IN, Pin.PULL_UP)
alarm_time = [0, 0, 0]


def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('Columbia University', '')
        # sta_if.connect('asussb', 'immortality')
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
    global record_state, show_gesture, gesture_str
    irq_state = machine.disable_irq()
    active = 0
    while active < 20:
        if p.value() == 0:
            active += 1
        else:
            return
        time.sleep_ms(1)

    show_gesture = True
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
    button_c.irq(trigger=Pin.IRQ_FALLING, handler=set_alarm)


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


def show_time():
    oled.fill(0)
    if rtc.datetime()[4] == alarm_time[0] and rtc.datetime()[5] == alarm_time[1] and rtc.datetime()[6] == alarm_time[2]:
        oled.text("it is alarm time", 0, 0)
        oled.show()
        time.sleep(2)
        oled.fill(0)
    cur_date = "date: " + str(rtc.datetime()[0]) + '/' + str(rtc.datetime()[1]) + '/' + str(rtc.datetime()[2])
    cur_time = "time: " + str(rtc.datetime()[4]) + ':' + str(rtc.datetime()[5]) + ':' + str(rtc.datetime()[6])
    oled.text(cur_date, 0, 0)
    oled.text(cur_time, 0, 10)
    if show_alarm:
        alarm_text = "alarm: " + str(alarm_time[0]) + ':' + str(alarm_time[1]) + ':' + str(alarm_time[2])
        oled.text(alarm_text, 0, 20)
    oled.show()


def set_alarm(p):
    # debounce
    global record_state, show_gesture, gesture_str, alarm_time
    irq_state = machine.disable_irq()
    active = 0
    while active < 20:
        if p.value() == 0:
            active += 1
        else:
            return
        time.sleep_ms(1)

    if alarm_time[2] >= 55:
        alarm_time[2] = 0
        alarm_time[1] += 1
    else:
        alarm_time[2] += 5

    machine.enable_irq(irq_state)


reallocate()
ip_addr = do_connect()
print(ip_addr)
# data format
write(0x31, 0x01)
# power ctl
write(0x2D, 0x08)
button_b.irq(trigger=Pin.IRQ_FALLING, handler=record)
button_c.irq(trigger=Pin.IRQ_FALLING, handler=set_alarm)

socket_addr = usocket.getaddrinfo(ip_addr[0], 80)[0][-1]
s_listening = usocket.socket()
s_listening.bind(socket_addr)
s_listening.listen(5)
s_listening.settimeout(0.5)
print('listening on', socket_addr)


letter_list = []
while True:
    for i in range(4000):
        if record_state == 1:
            x, y, _ = get_pos()
            letter_list.append([x, y])
            time.sleep(0.05)

        if record_state == 0:
            send_list = generate_clean_list(letter_list)
            if len(send_list) < 20:
                record_state = -1
                continue
            else:
                post_list = []
                for j in range(20):
                    cx = send_list[j][0]
                    cy = send_list[j][1]
                    post_list.append(cx)
                    post_list.append(cy)

                server_addr = socket.getaddrinfo('52.90.217.13', 8080)[0][-1]

                s_reading = socket.socket()
                s_reading.connect(server_addr)

                s_reading.send(str.encode(str(post_list)))

                result = s_reading.recv(10)

                s_reading.close()
                gesture_str = result
                print(gesture_str)

                record_state = -1
                letter_list = []

        if record_state == -1:
            break

    try:
        cl, addr = s_listening.accept()

    except OSError:
        if display:
            if show_gesture:
                oled.fill(0)
                oled.text(gesture_str, 0, 0)
                oled.show()
            elif show_time_now:
                show_time()
            oled.contrast(1000 * adc.read())

    else:
        print('client connected from', addr)
        request = cl.recv(1024)
        request = str(request)
        print('content = %s' % request)

        if 'msg' in request:
            msg = request.split('/?msg=')[1].split('HTTP')[0].replace('%20', ' ')
            if 'on' in msg:
                show_gesture = False
                display = True
            elif 'off' in msg:
                display = False
                oled.fill(0)
                oled.show()
            elif 'twitter' in msg:
                text_msg = msg.split('twitter')[1].strip()
                twitter_url = "https://api.thingspeak.com/apps/thingtweet/1/statuses/update?api_key=%s&status=%s" % \
                              ("PEJRWV7OWH9FCK12", text_msg)
                _, _, t_host, t_path = twitter_url.split('/', 3)
                twitter_addr = usocket.getaddrinfo(t_host, 80)[0][-1]
                s_sending = usocket.socket()
                s_sending.connect(twitter_addr)
                s_sending.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (t_path, t_host), 'utf8'))
            elif 'time' in msg:
                time_digits = msg.split("=")[1].split("-")
                msg = "show time now"
                rtc.datetime((int(time_digits[0]), int(time_digits[1]), int(time_digits[2]), 0, int(time_digits[3]),
                              int(time_digits[4]), int(time_digits[5]), 0))
            elif 'weather' in msg:
                weather_list = msg.split('%0A')
                msg = 'show weather'
            elif 'alarm' in msg:
                msg = "show alarm"
                alarm_time = [rtc.datetime()[4], rtc.datetime()[5], rtc.datetime()[6]]
                show_alarm = True

            if 'time' in msg or 'alarm' in msg:
                show_gesture = False
                show_time_now = True
            else:
                show_time_now = False

            if display:
                oled.fill(0)
                if msg == 'show weather':
                    oled.text("weather: ", 0, 0)
                    oled.text(weather_list[0].split(':')[1].strip(), 0, 10)
                    oled.text(weather_list[1], 0, 20)
                elif 'twitter' in msg:
                    oled.text('send twitter:', 0, 0)
                    oled.text(text_msg, 0, 10)
                else:
                    oled.text(msg, 0, 0)
                oled.show()
                oled.contrast(1000 * adc.read())

            suc_response = "HTTP/1.1 200 OK\r\n\r\n%s" % msg
            cl.send(str.encode(suc_response))

        else:
            fail_response = "HTTP/1.1 501 Implemented\r\n\r\nPlease attach msg!"
            cl.send(str.encode(fail_response))

        cl.close()




