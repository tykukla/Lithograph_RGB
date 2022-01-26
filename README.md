# Lithograph_RGB
Two versions of a lithograph with Neopixel RGB backlights. One with a rotary encoder to select the hue, saturation, and value. The other with multiple panels and a push-button to randomly select a color for each panel (or cycle between random colors).

## Introduction
This is a hobby project, no science here!

This project creates lithographic displays that are backlit by LED strips using a either an Adafruit RP2040 Feather or a Raspberry Pi Pico (code available for both). There is also a single-panel and a multi-panel option. 

I used https://3dp.rocks/lithophane/ to make the lithophanes. 

There are many variations of similar projects on the web. A recent one (at time of writing) that is more practical and sophisticated was highlighted by Raspberry Pi here: https://www.raspberrypi.com/news/illuminate-the-way-with-the-adjustable-picolight/.


## Single-Panel version -- How it works
Here, a lithograph is separated from a backplate using stand-offs and neodymium magnets. The magnets allow for some adjustment and also make it possible to remove the backplate and prop the lithograph up on a stand-off or two by itself for natural light use. The backplate has a Neopixel RGB LED strip (**WS2812B**) facing the lithograph and a rotary encoder, on/off switch, and microcontroller on the other side. I made no effort to hide the wires here. Instead I tried to keep the wiring neat because I like how it looks (...at least when I can keep the wiring neat, which you may find is rarely).

The rotary encoder cycles through HSV (hue, saturation, value) colors. Pressing the rotary encoder cycles between each. 


## Multi-Panel version -- How it works
This is an Andy Warhol-inspired lithograph project. Each panel has an RGB LED strip behind it that displays a given color, and each panel's color is selected randomly upon pressing a push-button. Holding the push-button for three seconds changes the mode to randomly display new colors after some amount of time (60 seconds in my code). Holding for three seconds again returns to the mode where the same random colors persist indefinitely. To prevent displaying colors that are too similar, the colors are selected by a function that randomly imposes some minimum distance between the hue of any two colors (brightness (or value) and saturation are the same for all colors). 

The basic construction is very similar to the single-panel version, although the backplate has sub-divisions that separate the light for each panel. 

## What you'll find here
This repository contains the necessary code (in CircuitPython), wiring diagrams, .stl files, and photos of example results. 

## Room for improvement
There is a lot that could be done to improve this project! A few things off the top of my head that you may want to consider

* **Dynamic colors**: Right now, when a color is selected it remains constant, which is boring. It would be cool to add some random noise / undulations to the saturation and/or brightness of the selected hue (although this may render the saturation and brightness selection options useless). 
* **Color memory**: If a user has a favorite color, they have to navigate to that color every time they turn on the RGBs. A better approach is to save the last color on shut-down so it becomes the first color displayed at the next startup. 

Please reach out if you have any questions! 



