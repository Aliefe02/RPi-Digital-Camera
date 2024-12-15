#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import time
import logging
from gpiozero import Button
from picamera2 import Picamera2, Preview
from PIL import Image
import RPi.GPIO as GPIO

# Add the LCD library path
sys.path.append("/home/ali/Camera_Project/LCD_Module_RPI_code/RaspberryPi/python/")
from LCD_Module_RPI_code.RaspberryPi.python.lib import LCD_1inch69

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

# Folder to save photos
PHOTOS_FOLDER = "/home/ali/Camera_Project/photos/"
os.makedirs(PHOTOS_FOLDER, exist_ok=True)

# Function to take a photo
def take_photo(camera, disp, size):
    timestamp = int(time.time())
    photo_path = f"{PHOTOS_FOLDER}{timestamp}.jpg"
    camera.capture_file(photo_path)
    print(f"Photo saved: {photo_path}")
    display_photo(disp, photo_path, size)
    return photo_path

# Function to display an image on the LCD
def display_photo(disp, photo_path, size):
    image = Image.open(photo_path)
    image = image.resize(size)
    image = image.rotate(270)
    disp.ShowImage(image)

# Function to stream live preview to the display
def stream_live_feed(disp, camera, size):
    print("Starting live feed")
    while True:
        # Capture the live feed frame
        frame = camera.capture_array()
        image = Image.fromarray(frame)
        image = image.resize(size)
        image = image.rotate(270)
        disp.ShowImage(image)

        # Exit live feed on button press
        if GPIO.input(touchpin) == 1 or button_top.is_pressed:
            print("Exiting live feed")
            return
        time.sleep(0.01)

# Function to walk through the gallery
def walk_gallery(disp, size):
    print("Entering gallery mode")
    photos = os.listdir(PHOTOS_FOLDER)
    photos.sort()
    if not photos:
        print("No photos to display")
        disp.clear()
        return

    i = len(photos) - 1
    display_photo(disp, PHOTOS_FOLDER + photos[i], size)
    while True:
        time.sleep(0.2)
        if button_top.is_pressed:
            disp.clear()
            return
        elif GPIO.input(touchpin) == 1 and button_left.is_pressed:
            print(f"Deleting {photos[i]}")
            os.remove(PHOTOS_FOLDER + photos[i])
            photos = os.listdir(PHOTOS_FOLDER)
            photos.sort()
            if i >= len(photos):
                i = 0
        elif button_right.is_pressed:
            i = (i + 1) % len(photos)
        elif button_left.is_pressed:
            i = (i - 1) % len(photos)

        try:
            # Attempt to display the current photo
            display_photo(disp, PHOTOS_FOLDER + photos[i], size)
        except Exception as e:
            # If photo is corrupted, delete it and move on to the next one 
            print(f"Error displaying image {photos[i]}: {e}")
            os.remove(PHOTOS_FOLDER + photos[i])
            photos = os.listdir(PHOTOS_FOLDER)
            photos.sort()
            if i >= len(photos):
                i = 0

try:
    print("Booting...")
    # Initialize display
    disp = LCD_1inch69.LCD_1inch69()
    disp.Init()
    disp.clear()
    disp.bl_DutyCycle(50)

    # Initialize camera
    print("Initializing camera")
    camera = Picamera2()
    config = camera.create_preview_configuration(main={"size": (640, 480)})
    camera.configure(config)
    camera.start()

    size = (240, 280)  # LCD screen resolution

    print("Ready! Press the button to take a photo or view the gallery.")
    while True:
        stream_live_feed(disp, camera, size)
        if GPIO.input(touchpin) == 1:
            take_photo(camera, disp, size)
            time.sleep(2)
        elif button_top.is_pressed:
            walk_gallery(disp, size)
        time.sleep(0.2)

except Exception as e:
    print("Error:", e)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    disp.module_exit()
    camera.stop()
    exit()
