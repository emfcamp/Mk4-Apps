"""This app needs an SDS011 sensor attacthed to UART 4 """

___name___         = "Air Quality"
___license___      = "MIT"
___dependencies___ = ["sleep", "app", "ugfx_helper", "buttons", "homescreen"]
___categories___   = ["EMF"]
___bootstrapped___ = False # Whether or not apps get downloaded on first install. Defaults to "False", mostly likely you won't have to use this at all.

import app 
import ugfx, os, time, sleep
from tilda import Buttons
from tilda import Sensors
from machine import Pin
from machine import UART
from machine import Neopix
import random

class DustSensorTester(object):

    verbose = False

    def contains_sequence (self,data, test):
        """ Checks to see if the data sequence contains the test sewquence

        Args:
            data: sequence of data items
            test: test sequence
        Returns:
            True if the test sequence is in the data sequence
        """

        if len(data)<len(test): return False

        for pos in range(0,len(data)-len(test)+1):
            if test == data[pos:pos+len(test)]: return True
        return False

class DustSensor(object):

    verbose = False
    fake_sensor = False

    AWAITING_START = 0
    READING_BLOCK = 1

    def pump_byte(self, b):
        """ Pump a byte into the block decode. Calls the decode method
            when the block is complete

        Args:
            b: byte to pump
        """
        if self.state==self.AWAITING_START:
            if self.verbose: print(self, "Awaiting start:", b)
            if b==self.start_sequence[self.start_pos]:
                # got a match - move to next byte in start sequence
                self.start_pos = self.start_pos+1
                if self.start_pos == len(self.start_sequence):
                    # matched the start sequence
                    self.block=self.start_sequence.copy()
                    self.state=self.READING_BLOCK
        elif self.state==self.READING_BLOCK:
            if self.verbose: print("Reading block:", b)
            self.block.append(b)
            if len(self.block) == self.block_size:
                self.state=self.AWAITING_START
                self.start_pos=0
                self.process_block()

    def __init__(self, display):
        self.display = display
        self.state=self.AWAITING_START
        self.start_pos = 0

class sds011_sensor(DustSensor):
    start_sequence = [0xaa,0xc0]
    block_size = 10

    def process_block(self):
        """ Process a block of data obtained from the sensor
            calls the new_reading method on the display to 
            deliver a new reading or the error method
            on the display to indicate an error
        """
        if self.verbose: print("sds011 process block")
        if self.verbose: print([hex(x) for x in self.block])
        check_sum = 0
        for i in range(2,8):
            check_sum = check_sum + self.block[i]
        check_sum = check_sum & 0xff
        if self.verbose: print("Checksum:",hex(check_sum))
        if check_sum!=self.block[8]:
            message = "Rcv:" + hex(self.block[8]) + " Cal:" + hex(check_sum)
            self.display.error(message)
            return
        ppm10 = (self.block[4]+256*self.block[5])/10
        ppm2_5 = (self.block[2]+256*self.block[3])/10
        self.display.new_readings(ppm10,ppm2_5)
    
class Air_Quality_Display():
    
    def setup_screen(self):
        """ Set up the screen and the labels that display
            values on it. 
        """
        ugfx.init()
        width=ugfx.width()
        height=ugfx.height()
        ugfx.clear(ugfx.html_color(0x800080))
        style = ugfx.Style()
        style.set_enabled([ugfx.WHITE, ugfx.html_color(0x800080), ugfx.html_color(0x800080), ugfx.html_color(0x800080)])
        style.set_background(ugfx.html_color(0x800080))
        ugfx.set_default_style(style)
        ugfx.orientation(90)
        ugfx.set_default_font(ugfx.FONT_TITLE)
        ugfx.Label(0, 0, width, 60,"Air Quality", justification=ugfx.Label.CENTER)
        label_height=45
        self.ppm10_label = ugfx.Label(0, label_height, width, label_height,"PPM 10: starting", justification=ugfx.Label.CENTER)
        self.ppm25_label = ugfx.Label(0, label_height*2, width, label_height,"PPM 2.5: starting", justification=ugfx.Label.CENTER)

        self.temp_label = ugfx.Label(0, label_height*3, width, label_height,"Temp: starting", justification=ugfx.Label.CENTER)
        self.humid_label = ugfx.Label(0, label_height*4, width, label_height,"Humid: starting", justification=ugfx.Label.CENTER)
        self.error_label = ugfx.Label(0, label_height*5, width, label_height,"", justification=ugfx.Label.CENTER)
        self.message_label = ugfx.Label(0, label_height*6, width, label_height,"", justification=ugfx.Label.CENTER)
        self.error_count = 0
        self.error_message = ""
        self.neopix = Neopix()
        self.p10_decode = ((100,0x00ff00),(250,0xffff00),(350,0xff8000),(430,0xff0000),(-1,0xcc6600))
        self.p25_decode = ((60, 0x00ff00),(91, 0xffff00), (121,0xff8000),(251,0xff0000),(-1,0xcc6600))

    def get_reading_color(self, value, decode):
        for item in decode:
            if item[0] < 0:
                # reached the upper limit - return
                return item[1]
            if value < item[0]:
                return item[1]
    
    def new_readings(self,ppm10_value, ppm25_value):
        """ Called by the sensor to deliver new values to the screen.
            Will also trigger the reading of the temperature and humidity
            values.
        """
        self.ppm10_label.text("PPM 10: "+str(ppm10_value))
        self.ppm25_label.text("PPM 2.5: "+str(ppm25_value))
        temp = Sensors.get_hdc_temperature()
        temp_string = "Temp: {0:2.1f}".format(temp)
        self.temp_label.text(temp_string)
        humid = Sensors.get_hdc_humidity()
        humid_string = "Humidity: {0:2.1f}".format(humid)
        self.humid_label.text(humid_string)
        # Calculate some colours
        self.neopix.display((self.get_reading_color(ppm25_value, self.p25_decode),self.get_reading_color(ppm10_value, self.p10_decode)))

    def error(self, error_message):
        """ Called by the sensor to deliver an error message. 
        Args:
            error_message: error message string
        """
        self.error_count = self.error_count + 1
        self.error_label.text( "Errors: " +str(self.error_count))
        self.message_label.text(str(error_message))

display = Air_Quality_Display()
display.setup_screen()

sensor_port = UART(2,9600, bits=8, mode=UART.BINARY, parity=None, stop=1)

sensor = sds011_sensor(display)

def test_sensor():
    """ Can be called to pump some test sequences into the sensor
    """


    test_sequences = [ ['0xaa', '0xc0', '0xf', '0x0', '0x22', '0x0', '0xe1', '0xdb', '0xed', '0xab'],
        ['0xaa', '0xc0', '0x13', '0x0', '0x3e', '0x0', '0xe1', '0xdb', '0xb', '0xab'], # bad checksum
        ['0xaa', '0xc0', '0x13', '0x0', '0x3e', '0x0', '0xe1', '0xdb', '0xa', '0xab'],
        ['0xaa', '0xc0', '0x13', '0x0', '0x3e', '0x0', '0xe1', '0xdb', '0xd', '0xab'] ]

    for test_sequence in test_sequences:
        for ch in test_sequence:
            sensor.pump_byte(int(ch))

# test_sensor()

buffer = bytearray([0])

while (not Buttons.is_pressed(Buttons.BTN_A)) and (not Buttons.is_pressed(Buttons.BTN_B)) and (not Buttons.is_pressed(Buttons.BTN_Menu)):
    while sensor_port.any() > 0:
        sensor_port.readinto(buffer,1)
        sensor.pump_byte(buffer[0])
    sleep.wfi()

ugfx.clear()

app.restart_to_default()

