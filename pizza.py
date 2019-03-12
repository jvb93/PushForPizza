
from gpiozero import Button
from signal import pause
from numpy import interp
import colorsys
import time
import board
import neopixel
import configparser
from pizzapi import *



num_pixels = 8
hold_time_max = 3.0
pixel_pin = board.D18
ORDER = neopixel.RGB
use_button=27
config = configparser.ConfigParser()
config.read('config.ini')
config = config['DEFAULT']

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER)

held_for=0.0

def rls():
    global held_for
    print(held_for)
    if (held_for >= hold_time_max):
        startOrder()
    held_for = 0.0
    clearPixels()

def hld():
    # callback for when button is held
    #  is called every hold_time seconds
    global held_for
    # need to use max() as held_time resets to zero on last callback
    held_for = max(held_for, button.held_time + button.hold_time)
    if(held_for > hold_time_max):
        held_for = hold_time_max
    print(held_for)
    setColor(mapPercentageColor((held_for/hold_time_max)*100), -1)

def showSuccess():
    for x in range(10):
        rainbow_cycle(.001)

def setColor(color, pixel):
    if pixel < 0:
        pixels.fill(color)
    else:
        pixels[pixel] = color
    pixels.show()    
    
def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)

def mapPercentageColor(percent):
    hue = interp(percent,[0,100],[0,120])
    return hsv_to_rgb(hue/360.,1,1)

def hsv_to_rgb(h, s, v):
        if s == 0.0: v*=255; return (v, v, v)
        i = int(h*6.) # XXX assume int() truncates!
        f = (h*6.)-i; p,q,t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f)))); v*=255; i%=6
        if i == 0: return (v, t, p)
        if i == 1: return (q, v, p)
        if i == 2: return (p, v, t)
        if i == 3: return (p, q, v)
        if i == 4: return (t, p, v)
        if i == 5: return (v, p, q)

def clearPixels():
    setColor((0,0,0),-1)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos*3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos*3)
        g = 0
        b = int(pos*3)
    else:
        pos -= 170
        r = 0
        g = int(pos*3)
        b = int(255 - pos*3)
    return (r, g, b) if ORDER == neopixel.RGB or ORDER == neopixel.GRB else (r, g, b, 0)

def startOrder():
        print('order starting')
        customer = Customer(config['first_name'], config['last_name'], config['email'], config['phone'])
        address = Address(config['street_address'], config['city'], config['state_code'], config['zip'])
        store = address.closest_store()
       
        order = Order(store, customer, address)

        order.add_item(config['order_item'])

        response = 0
        if(config['production'] == "1"):
            card = PaymentObject(config['card_number'], config['expiry'], config['cvc'], config['card_zip'])
            response = order.place(card)
        else:
            response = order.pay_with()
        print(response)

clearPixels()
button=Button(use_button, hold_time=0.1, hold_repeat=True)
button.when_held = hld
button.when_released = rls

print('ready')
pause() # wait forever

