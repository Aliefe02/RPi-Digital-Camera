#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
from gpiozero import Button
from picamzero import Camera
import os
import sys
import time
import logging
import spidev as SPI
sys.path.append("/home/ali/Camera_Project/LCD_Module_RPI_code/RaspberryPi/python/")
from LCD_Module_RPI_code.RaspberryPi.python.lib import LCD_1inch69
from PIL import Image, ImageDraw, ImageFont, ImageOps
import RPi.GPIO as GPIO

# Tactile buttons configurations
button_top = Button(20)
button_left = Button(21)
button_right = Button(16)


# Raspberry Pi pin configuration:
RST = 27
DC = 25
BL = 18
bus = 0
device = 0


# Touch button configuration for taking photo
GPIO.setmode(GPIO.BCM)
touchpin = 23

GPIO.setup(touchpin, GPIO.IN)

PHOTOS_FOLDER = "/home/ali/Camera_Project/photos/"

def take_photo(camera):
    timestamp = int(time.time())
    photo_name = f"{PHOTOS_FOLDER}{timestamp}.jpg"
    camera.take_photo(photo_name)
    return photo_name

def display_photo(disp, photo_name, size):
    image = Image.open(photo_name)
    image = image.resize(size)
    image = image.rotate(270)

    disp.ShowImage(image)

def walk_gallery(disp, size):
    print("walk gallery mode")
    photos = os.listdir(PHOTOS_FOLDER)
    photos.sort()
    i = 0
    display_photo(disp, PHOTOS_FOLDER + photos[0], size)
    while True:
        display_new = False
        time.sleep(.2)
        if button_top.is_pressed:
            # Return button is pressed, go back to taking photo mode
            disp.clear()
            return
        elif GPIO.input(touchpin) == 1 and button_left.is_pressed:
            # Delete current photo
            print(f"Deleting {photos[i]}")
            os.remove(PHOTOS_FOLDER + photos[i])
            photos = os.listdir(PHOTOS_FOLDER)
            photos.sort()

            if i>=len(photos):
                i = 0
            display_new = True

        elif button_right.is_pressed:
            # Go to next photo
            i += 1
            if i >= len(photos): # If reached to the last photo, go to start
                i = 0
            display_new = True

        elif button_left.is_pressed:
            # Go to previous photo
            i -= 1
            if i < 0: # If previous of the first photo, go to last last photo
                i = len(photos) - 1
            display_new = True



        if display_new:
            display_photo(disp, PHOTOS_FOLDER + photos[i], size)


try:
    print("Booting")
    # display with hardware SPI:
    disp = LCD_1inch69.LCD_1inch69()
    # Initialize library.
    disp.Init()
    # Clear display.
    disp.clear()
    #Set the backlight to 100
    disp.bl_DutyCycle(50)

    size = (240, 280)
    print("Accessing camera")
    camera = Camera()
    camera.still_size = (1200, 1400)
    print("Take picture")
    while True:
        if GPIO.input(touchpin) == 1:
            print("Taking photo")
            photo_name = take_photo(camera)
            display_photo(disp, photo_name, size)

        elif button_top.is_pressed:
            walk_gallery(disp, size)
            print("Returned to take photo mode")


        time.sleep(.2)

    disp.module_exit()

except IOError as e:
    print("Error",e)

except KeyboardInterrupt:
    print("Keyboard Interrupt\n Quitting...")
    disp.module_exit()
    exit()
