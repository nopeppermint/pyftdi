# Copyright (c) 2014-2016, Emmanuel Blot <emmanuel.blot@free.fr>
# Copyright (c) 2016, Emmanuel Bouaziz <ebouaziz@free.fr>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Neotion nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL NEOTION BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from pyftdi.ftdi import Ftdi
from struct import pack as spack


__all__ = ['GpioController']


class GpioException(IOError):
    """Base class for GPIO errors"""


class GpioController(object):
    """GPIO controller for an FTDI port"""

    MASK = 0xff

    def __init__(self):
        self._ftdi = None
        self._direction = 0

    @property
    def direction(self):
        return self._direction

    @property
    def is_connected(self):
        return bool(self._ftdi)

    def open_from_url(self, url, direction, **kwargs):
        """
        """
        for k in ('direction',):
            if k in kwargs:
                del kwargs[k]
        try:
            ftdi = Ftdi()
            ftdi.open_bitbang_from_url(url, direction=direction, **kwargs)
            self._ftdi = ftdi
        except IOError as e:
            raise GpioException('Unable to open USB port: %s' % str(e))
        self._direction = direction

    def close(self):
        """Close the FTDI interface"""
        if self._ftdi:
            self._ftdi.close()
            self._ftdi = None

    def set_direction(self, direction):
        """Update the GPIO pin direction.

           :param direction: a bitfield of GPIO pins. Each bit represent a GPIO
                             pin, where '1' sets the pin as output and '0' sets
                             the pin as input/high-Z.
        """
        if direction > self.MASK:
            raise GpioException("Invalid direction mask")
        self._direction = direction
        self._ftdi.set_bitmode(self.direction, Ftdi.BITMODE_BITBANG)

    def read_port(self):
        """Read the GPIO input pin electrical level.

           :param value: a bitfield of GPIO pins. Each bit represent a GPIO
                         pin, where '1' sets the pin to high level and '0'
                         sets the pin to low level. GPIO pins that are
                         configured as Input are left unaltered.
        """
        if not self.is_connected:
            raise GpioException('Not connected')
        return self._ftdi.read_pins()

    def write_port(self, value):
        """Set the GPIO output pin electrical level.

           :param value: a bitfield of GPIO pins. Each bit represent a GPIO
                         pin, where '1' reports a high level on the matching
                         pin and '0' reports a low level. GPIO pins that are
                         configured as Output should be ignored.
        """
        if not self.is_connected:
            raise GpioException('Not connected')
        if value > self._direction or (value & ~self._direction):
            raise GpioException("Invalid value")
        self._ftdi.write_data(spack('<B', value))
