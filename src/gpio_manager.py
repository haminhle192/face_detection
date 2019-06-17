__author__ = 'vietbq'

import RPi.GPIO as GPIO
import time

light_1_pin = 11
light_2_pin = 11

class GPIO_Manager:

    def __init__(self):
        GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
        GPIO.setup(light_1_pin, GPIO.OUT)
        GPIO.setup(light_2_pin, GPIO.OUT)
        GPIO.output(light_1_pin, GPIO.LOW)
        GPIO.output(light_2_pin, GPIO.LOW)
        self.start_on= 0
        self.on = False
        print('GPIO Manager initialed')

    def turn_on(self):
        if not self.on:
            print('Turn on the light')
            self.on = True
            self.start_on = time.time()
            GPIO.output(light_1_pin, GPIO.HIGH)
        else:
            print('The light was on')

    def turn_off(self):
        GPIO.output(light_1_pin, GPIO.LOW)

    def cleanup(self):
        GPIO.cleanup()