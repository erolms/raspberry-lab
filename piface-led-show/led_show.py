#!/usr/bin/env python3

import sys
import time
import threading
import random
import pifacedigitalio

class LedController:
    """Simple Class to controll the LED show behaviour"""
    def __init__(self):
        self.rnd = 0
        self.odd_led = 0
        self.even_led = 0
        self.all_at_once = 0
        self.last_light = -1
        self.sleep = 0.5

def init_lights():
    """Initialize LEDs from 0-7 before starting with the show"""
    global pif
    for x in range(8):
        pif.leds[x].turn_on()
        time.sleep(0.05)
        pif.leds[x].turn_off()
    for x in range(7, -1, -1):
        pif.leds[x].turn_on()
        time.sleep(0.05)
        pif.leds[x].turn_off()

def blink_led(id):
    """Blink specified LED"""
    global pif
    pif.leds[id].turn_on()
    time.sleep(ledc.sleep)
    pif.leds[id].turn_off()

def blink_all_led():
    """Blink all LEDs in range minding odd and even parameters"""
    global pif, ledc
    if ledc.even_led == 1:
        start = 0
        incr = 2
    elif ledc.odd_led == 1:
        start = 1
        incr = 2
    else:
        start = 0
        incr = 1
    for x in range(start, 8, incr):
        pif.leds[x].turn_on()
    time.sleep(ledc.sleep)
    for x in range(start, 8, incr):
        pif.leds[x].turn_off()

def led_blinker():
    """method to blink LED lights based on the parameters

    Method led_blinker will read the parameters from the ledc global class
    and based on the setting blink the LEDs. Parameters are changed by
    pressing the switches on the PiFace.
    """
    while True:
        global ledc
        if ledc.rnd == 1:
            ledc.last_light = random.randint(0, 7)
            blink_led(ledc.last_light)
        elif ledc.all_at_once == 1:
            blink_all_led()
        elif ledc.even_led == 1:
            if ledc.last_light % 2 == 0:
                ledc.last_light += 2
            else:
                ledc.last_light += 1
            if ledc.last_light >= 7:
                ledc.last_light = 0
            blink_led(ledc.last_light)
        elif ledc.odd_led == 1:
            if ledc.last_light % 2 == 0:
                ledc.last_light += 1
            else:
                ledc.last_light += 2
            if ledc.last_light > 7:
                ledc.last_light = 1
            blink_led(ledc.last_light)
        else: # blink all one by one
            ledc.last_light += 1
            if ledc.last_light > 7:
                ledc.last_light = 0
            blink_led(ledc.last_light)
        time.sleep(ledc.sleep)

def toggle_rnd(event):
    global ledc
    if ledc.rnd == 1:
        ledc.rnd = 0
    else:
        ledc.rnd = 1
        ledc.all_at_once = 0

def toggle_all_lights(event):
    global ledc
    if ledc.all_at_once == 1:
        ledc.all_at_once = 0
    else:
        ledc.all_at_once = 1
        ledc.rnd = 0

def toggle_odd_lights(event):
    global ledc
    if ledc.odd_led == 1:
        ledc.odd_led = 0
    else:
        ledc.odd_led = 1
        ledc.even_led = 0

def toggle_even_lights(event):
    global ledc
    if ledc.even_led == 1:
        ledc.even_led = 0
    else:
        ledc.even_led = 1
        ledc.odd_led = 0

def cleanup():
    """Cleanup method on Ctrl+C"""
    global ledc, pif, switch_listener
    switch_listener.deactivate()
    for x in range(8):
        pif.leds[x].turn_off()
    pif.deinit_board()
    print ("")
    print ("PiFace cleanup complete.")

def main():
    global pif, ledc, switch_listener
    try:    # initialize board and bail if it fails
        pif = pifacedigitalio.PiFaceDigital()
    except:
        print ("Could not initialize board, bailing.")
        sys.exit(1)

    try:    # initialize LED state
        init_lights()
    except KeyboardInterrupt:
        cleanup()
        sys.exit(1)

    ledc = LedController()

    # setup Switch listeners
    switch_listener = pifacedigitalio.InputEventListener(chip=pif)
    switch_listener.register(0, pifacedigitalio.IODIR_FALLING_EDGE, toggle_rnd)
    switch_listener.register(1, pifacedigitalio.IODIR_FALLING_EDGE, toggle_all_lights)
    switch_listener.register(2, pifacedigitalio.IODIR_FALLING_EDGE, toggle_odd_lights)
    switch_listener.register(3, pifacedigitalio.IODIR_FALLING_EDGE, toggle_even_lights)
    switch_listener.activate()

    # spawn the LED blinker thread
    thr = threading.Thread(target=led_blinker, name=led_blinker)
    thr.daemon = True
    thr.start()

    while True:     # wait for Ctrl+C to stop the programm
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            cleanup()
            sys.exit(1)

if __name__ == '__main__':
    main()
