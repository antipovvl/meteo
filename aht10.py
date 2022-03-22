#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  aht10.py
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


import utime
from micropython import const


class AHT10:
    """Interface library for AHT10/AHT20 temperature+humidity sensors"""

    AHTX0_I2CADDR_DEFAULT = const(0x38)  # Default I2C address
    AHTX0_CMD_INITIALIZE = 0xE1  # Initialization command
    AHTX0_CMD_TRIGGER = const(0xAC)  # Trigger reading command
    AHTX0_CMD_SOFTRESET = const(0xBA)  # Soft reset command
    AHTX0_STATUS_BUSY = const(0x80)  # Status bit for busy
    AHTX0_STATUS_CALIBRATED = const(0x08)  # Status bit for calibrated

    def __init__(self, i2c, address=AHTX0_I2CADDR_DEFAULT):
        utime.sleep_ms(20)  # 20ms delay to wake up
        self._i2c = i2c
        self._address = address
        self._buf = bytearray(6)
        self.reset()
        if not self.initialize():
            raise RuntimeError("Could not initialize")
        self._temp = None
        self._humidity = None

    def reset(self):
        """Perform a soft-reset of the AHT"""
        self._buf[0] = self.AHTX0_CMD_SOFTRESET
        self._i2c.writeto(self._address, self._buf[0:1])
        utime.sleep_ms(20)  # 20ms delay to wake up

    def initialize(self):
        """Ask the sensor to self-initialize. Returns True on success, False otherwise"""
        self._buf[0] = self.AHTX0_CMD_INITIALIZE
        self._buf[1] = 0x08
        self._buf[2] = 0x00
        self._i2c.writeto(self._address, self._buf[0:3])
        self._wait_for_idle()
        if not self.status & self.AHTX0_STATUS_CALIBRATED:
            return False
        return True

    @property
    def status(self):
        """The status byte initially returned from the sensor, see datasheet for details"""
        self._read_to_buffer()
        # print("status: "+hex(self._buf[0]))
        return self._buf[0]

    @property
    def relative_humidity(self):
        """The measured relative humidity in percent."""
        self._perform_measurement()
        self._humidity = (self._buf[1] << 12) | (self._buf[2] << 4) | (self._buf[3] >> 4)
        self._humidity = (self._humidity * 100) / 0x100000
        return self._humidity

    @property
    def temperature(self):
        """The measured temperature in degrees Celcius."""
        self._perform_measurement()
        self._temp = ((self._buf[3] & 0xF) << 16) | (self._buf[4] << 8) | self._buf[5]
        self._temp = ((self._temp * 200.0) / 0x100000) - 50
        return self._temp

    def _read_to_buffer(self):
        self._i2c.readfrom_into(self._address, self._buf)
    
    def _trigger_measurement(self):
        """Internal function for triggering the AHT to read temp/humidity"""
        self._buf[0] = self.AHTX0_CMD_TRIGGER
        self._buf[1] = 0x33
        self._buf[2] = 0x00
        self._i2c.writeto(self._address, self._buf[0:3])

    def _wait_for_idle(self):
        while self.status & self.AHTX0_STATUS_BUSY:
            utime.sleep_ms(5)

    def _perform_measurement(self):
        self._trigger_measurement()
        self._wait_for_idle()
        self._read_to_buffer()


class AHT20(AHT10): 
    AHTX0_CMD_INITIALIZE = 0xBE  # Calibration command
