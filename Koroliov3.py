#! /usr/bin/python
# Based on code written by Dan Mandle http://dan.mandle.me September 2012
# License: GPL 2.0
 
from gps import *
from time import *
import time
import threading
 
import Adafruit_BMP.BMP085 as BMP085

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

gpsd = None #seting the global variable

BMP180_sensor = BMP085.BMP085()

OLED = Adafruit_SSD1306.SSD1306_128_32(rst=None)

# Initialize library.
OLED.begin()

# Clear display.
OLED.clear()
OLED.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = OLED.width
height = OLED.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)


# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding

# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()

class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true
 
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer
 
if __name__ == '__main__':
  gpsp = GpsPoller() # create the thread
  try:
    gpsp.start() # start it up
    while True:
      #It may take a second or two to get good data
      #print gpsd.fix.latitude,', ',gpsd.fix.longitude,'  Time: ',gpsd.utc
 
      gps_latitude = gpsd.fix.latitude
      gps_longitude = gpsd.fix.longitude
      gps_utc = gpsd.utc
      gps_time = gpsd.fix.time
      gps_altitude = gpsd.fix.altitude
      gps_sats = gpsd.satellites

      BMP180_temperature = '{0:0.2f}'.format(BMP180_sensor.read_temperature())
      BMP180_pressure = '{0:0.2f}'.format(BMP180_sensor.read_pressure())
      BMP180_altitude = '{0:0.2f}'.format(BMP180_sensor.read_altitude())
      BMP180_sea_level_pressure = '{0:0.2f}'.format(BMP180_sensor.read_sealevel_pressure())
 
      # Draw a black filled box to clear the image.
      draw.rectangle((0,0,width,height), outline=0, fill=0)

      # Write four lines of text.
      draw.text((x, top),       "T: " + BMP180_temperature + "C",  font=font, fill=255)
      draw.text((x, top+8),     "P: " + BMP180_pressure + "P", font=font, fill=255)
      draw.text((x, top+16),    "Lat: " + gps_latitude,  font=font, fill=255)
      draw.text((x, top+25),    "Lon: " + gps_longitude,  font=font, fill=255)

      # Display image.
      OLED.image(image)
      OLED.display()

      time.sleep(10) #set to whatever
 
  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print "\nKilling Thread..."
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doing
  print "Done.\nExiting."
