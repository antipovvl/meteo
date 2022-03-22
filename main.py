#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.py
#  
#  Copyright 2022 Valery <valery@laptop>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import micropython
import time
from bmp180 import BMP180
from aht10 import AHT10
from machine import I2C, Pin
from umqtt.simple import MQTTClient
import wi_fi
p12=Pin(12,Pin.OUT)
wi_fi.do_connect()
from wi_fi import mac
time.sleep(1)
p12.on()
rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
rtc.alarm(rtc.ALARM0, 7*60*1000)

def dev_scan():
	try:
		i2c = I2C(scl=Pin(5), sda=Pin(4))
		aht = AHT10(i2c)
		time.sleep(3)
		bmp180 = BMP180(i2c)
		bmp180.oversample_sett = 3
		bmp180.baseline = 101325
		pres = round((bmp180.pressure)/133.322)
		temp = aht.temperature
		hum = round(aht.relative_humidity,1)
		alt = bmp180.altitude
		dtemp = round((temp + (bmp180.temperature)) / 2,1)
		return [dtemp, pres, hum]
	except BaseException:
		print("Ошибка Датчика")
		time.sleep(120)
		dev_scan()       
def client_send(dtemp, pres, hum):
	try:
		time.sleep(3)
		print('mac:',mac)
		client=MQTTClient(mac, server='narodmon.ru', port=1883, user='username', password='password')
		client.connect()
		print('Temperature: ', dtemp)
		client.publish('valery/esp8266/temperature', str(dtemp))
		time.sleep(3)
		client.connect()
		print('Pressure: ', pres)
		client.publish('valery/esp8266/pressure', str(pres))
		time.sleep(3)
		client.connect()
		print('Humidity: ', hum)
		client.publish('valery/esp8266/humidity', str(hum))
		time.sleep(3)
	except OSError:
		print("Нет Передачи!")
		p12.off()
		time.sleep(10)
		client_send(dtemp, hum, pres)
		p12.on()
    #теперь при вызове deepsleep контроллер уснёт на 5 минут и загрузится заново, аналогично нажатию reset
    #не забудьте припаять wake на reset, на плате: GPIO16 и RST
x = dev_scan()
client_send(x[0], x[1], x[2])
machine.deepsleep()

