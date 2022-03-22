#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  wi_fi.py
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


def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Соединение с сетью...')
        sta_if.active(True)
        sta_if.connect('SSID', 'Password')
        while not sta_if.isconnected():
            pass
    print('Конфигурация сети:', sta_if.ifconfig())
    
import network
import ubinascii
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print(mac)
