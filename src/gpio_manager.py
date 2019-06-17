__author__ = 'vietbq'

import RPi.GPIO as GPIO
import time

light_1_pin = 10
light_2_pin = 11

class GPIO_Manager:

    def __init__(self):
        GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
        GPIO.setup(light_1_pin, GPIO.OUT) # LED pin set as output
        GPIO.setup(light_2_pin, GPIO.OUT) # PWM pin set as output
        self.start_on= 0

    def turn_on(self):
        self.start_on = time.time()
        GPIO.output(light_1_pin, GPIO.HIGH)

    def turn_off(self):
        GPIO.output(light_1_pin, GPIO.LOW)

    def cleanup(self):
        GPIO.cleanup()