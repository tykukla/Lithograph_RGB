
import time
import board
import digitalio
import rotaryio
import neopixel
import random
import adafruit_fancyled.adafruit_fancyled as fancy

## UPDATED ATTEMPT AT THE RGB WORK BUT THIS TIME USING HSV AND FANCYLED
#  -- HSV is like fancy.CHSV(0.1, 0.2, 0.3)  (all numbers 0-1)
#  -- where 0.1 is in the "Hue" space and can actually take on any non-integer
#  -- 0.2 is in the saturation space, determines how white the color is
#  -- 0.3 is in the value space and should determine darkness... 
#  == https://learn.adafruit.com/fancyled-library-for-circuitpython/colors 

# memory button 
button = digitalio.DigitalInOut(board.A3)
button.switch_to_input(pull=digitalio.Pull.UP)
# set button for encoder
# button = digitalio.DigitalInOut(board.D5) 
# button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP
button_state = None  # tracks the state of the button so that one press is only one press
button_mode = "push_cols"  # color changes when button is pressed (alternative is "random_cols" for cycling thru random colors)
cycle_rate = 60 * 10    # seconds times ten because we count in milliseconds (frequency colors change)
pixel_pin = board.A1
num_pixels = 8

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1.0, auto_write=False)
                           # pixel_order=(1, 0, 2, 3))


# ====================================================================================================================== # 
# :: CURRENTLY NOT IN USE ---------------------------------------------------------------------------------------------- # 
#
## Define matrices (one for R one for G one for B)
## with values from the grid shown here: https://www.rapidtables.com/web/color/RGB_Color.html
## This ALMOST follows the grid -- the greayscale column was moved to row 4 (idx = 3) (it's the same in all matrices) because it was surprising coming right after red
## --- RED
rmat = [  # each element is a row (constant brightness)
    [255, 255, 255, 255, 229, 204, 204, 204, 204, 204, 229, 255, 255],  # brightest 
    [255, 255, 255, 224, 204, 153, 153, 153, 153, 153, 204, 255, 255],  
    [255, 255, 255, 192, 178, 102, 102, 102, 102, 102, 178, 255, 255],
    [255, 255, 255, 160, 153, 51,  51,  51,  51,  51,  153, 255, 255],
    [255, 255, 255, 128, 128, 0,   0,   0,   0,   0,   123, 255, 255],
    [204, 204, 204, 96,  102, 0,   0,   0,   0,   0,   102, 204, 204],
    [153, 153, 153, 64,  76,  0,   0,   0,   0,   0,   76,  153, 153],
    [102, 102, 102, 32,  51,  0,   0,   0,   0,   0,   51,  102, 102],
    [51,  51,  51,  0,   25,  0,   0,   0,   0,   0,   25,  51,  51 ]   # darkest
]

## --- GREEN
gmat = [  # each element is a row (constant brightness)
    [204, 229, 255, 255, 255, 255, 255, 255, 229, 204, 204, 204, 204 ],  # brightest 
    [153, 204, 255, 224, 255, 255, 255, 255, 204, 153, 153, 153, 153 ],  
    [102, 178, 255, 192, 255, 255, 255, 255, 178, 102, 102, 102, 102 ],
    [51,  153, 255, 160, 255, 255, 255, 255, 153, 51,  51,  51,  51  ],
    [0  , 128, 255, 128, 255, 255, 255, 255, 128, 0,   0,   0,   0   ],
    [0  , 102, 204, 96,  204, 204, 204, 204, 102, 0,   0,   0,   0   ],
    [0  , 76,  153, 64,  153, 153, 153, 153, 76,  0,   0,   0,   0   ],
    [0  , 51,  102, 32,  102, 102, 102, 102, 51,  0,   0,   0,   0   ],
    [0  , 25,  51,  0,   51,  51,  51,  51,  25,  0,   0,   0,   0   ]   # darkest
]

## --- BLUE
bmat = [  # each element is a row (constant brightness)
    [204, 204, 204, 255, 204, 204, 229, 255, 255, 255, 255, 255, 229],  # brightest 
    [153, 153, 153, 224, 153, 153, 204, 255, 255, 255, 255, 255, 204],  
    [102, 102, 102, 192, 102, 102, 178, 255, 255, 255, 255, 255, 178],
    [51,  51,  51,  160, 51,  51,  153, 255, 255, 255, 255, 255, 153],
    [0  , 0,   0,   128, 0,   0,   128, 255, 255, 255, 255, 255, 127],
    [0  , 0,   0,   96,  0,   0,   102, 204, 204, 204, 204, 204, 102],
    [0  , 0,   0,   64,  0,   0,   76,  153, 153, 153, 153, 153, 76 ],
    [0  , 0,   0,   32,  0,   0,   51,  102, 102, 102, 102, 102, 51 ],
    [0  , 0,   0,   0,   0,   0,   25,  51,  51,  51,  51,  51,  25 ]   # darkest
]
# ====================================================================================================================== # 

startrow = 4  # 0 is bright, 8 is dark
startcol = 3  # 0 is red, grayscale is 3, blue is 8, 11 is pink, 
newcol = startcol
newrow = startrow
rowDirectionMultiplier = 1.0     # we can't loop for rows, we have to bounce back and forth, so this is done with this multiplier (either -1 or 1)

# thisR = rmat[startrow][startcol]
# thisG = gmat[startrow][startcol]
# thisB = bmat[startrow][startcol]
# thisCol = (thisR, thisG, thisB, 0)

## ============ HSV SETTINGS =============== ## 
HSVmax = 1.0  # max for each input
HSVmin = 0.0  # min for each input
## HUE
StepHue = 0.05  # step size for hue
thisHue = 0.33 # green is 0.33
newHue = thisHue  # initialize the toggle term
## SATURATION
thisSat = 1.0    # full is 1
## VALUE (Brightness)
thisValue = 0.6  # full is 1
## ========================================= ## 

### ============ RANDOMIZER FXN ============== ## 
### the goal is to get 4 quasi-random colors    
### around the hue wheel. One fully random, then 
### one random step size. The other step size is decided
### by 0.5-random step (where random step <0.5). 
### this means that step1 + step2 + step1 + step2 will always get you
### all the way around the circle and you can use step randomization
### parameters to set min distances the colors must be

def randomizer(stepMin, colsaturation, colvalue):
    ## [1] get random step size and calculate other step size
    step1 = random.uniform(stepMin, (0.5 - stepMin))
    step2 = 0.5 - step1
    ## [2] select random color to anchor you in some corner (0-1)
    randCol1 = random.random()
    randCol2 = randCol1 + step1
    randCol3 = randCol2 + step2
    randCol4 = randCol3 + step1
    ## [3] get the HSV colors
    col1 = fancy.CHSV(randCol1, colsaturation, colvalue)
    col2 = fancy.CHSV(randCol2, colsaturation, colvalue)
    col3 = fancy.CHSV(randCol3, colsaturation, colvalue)
    col4 = fancy.CHSV(randCol4, colsaturation, colvalue)
    # first box
    pixels[0] = col1.pack()
    pixels[1] = col1.pack()
    # second box
    pixels[2] = col2.pack()
    pixels[3] = col2.pack()
    # third box
    pixels[4] = col3.pack()
    pixels[5] = col3.pack()
    # fourth box
    pixels[6] = col4.pack()
    pixels[7] = col4.pack()
    pixels.show()





while True:

    # RANDOMIZER FXN
    # randomizer(stepMin=0.15, colsaturation=thisSat, colvalue=thisValue)
    
    # [ UPDATE COLORS ONLY ON BUTTON PRESS ]
    while button_mode == "push_cols":
        if button.value and button_state is None:  # button state is ready to be pressed
            button_state = "pressed"
        if not button.value and button_state == "pressed": # SELECT 4 RANDOM COLORS
            cur_value = button.value 
            prev_value = button.value
            idx = 1
            while cur_value == prev_value: # count to three
                idx = idx + 1
                time.sleep(0.1)  # quick break to keep time
                cur_value = button.value
                print(idx)
                if idx >= 30:  # three seconds
                    button_mode = "random_cols"
                    prev_value = "off"  # exit while loop
                    main_idx = 1 # prepare for random_cols loop

            ## === SELECT COLORS === ## 
            # RANDOMIZER FXN
            randomizer(stepMin=0.15, colsaturation=thisSat, colvalue=thisValue)

            print(button_mode)
            print(button_state)
            button_state = None
            
            time.sleep(0.1)
    
    # [ RANDOMLY UPDATE COLORS EVERY ''CYCLE_RATE'' MILLISECS ]
    while button_mode == "random_cols":
        # RANDOMIZER FXN
        if main_idx == 0 or main_idx % cycle_rate == 0:  # if initial or if divisible by the cycle rate seconds
            randomizer(stepMin=0.15, colsaturation=thisSat, colvalue=thisValue)
        
        if button.value and button_state is None:  # button state is ready to be pressed
            button_state = "pressed"
        if not button.value and button_state == "pressed": # SELECT 4 RANDOM COLORS
            cur_value = button.value 
            prev_value = button.value
            idx = 1
            while cur_value == prev_value: # count to three
                idx = idx + 1
                print(idx)
                time.sleep(0.1)  # quick break to keep time
                cur_value = button.value
                if idx >= 30:  # three seconds
                    button_mode = "push_cols"
                    prev_value = "off"  # exit while loop
                    randomizer(stepMin=0.15, colsaturation=thisSat, colvalue=thisValue) # show that we've switched
            
        main_idx = main_idx + 1
        print(main_idx)
        if main_idx == cycle_rate * 3:
            main_idx = 0  # reset just so numbers don't get crazy high
        time.sleep(0.1)


    
    # now the button
    
    
    
    # time.sleep(10)






# def colorwheel(pos):
#     # Input a value 0 to 255 to get a color value.
#     # The colours are a transition r - g - b - back to r.
#     if pos < 0 or pos > 255:
#         return (0, 0, 0, 0)
#     if pos < 85:
#         return (255 - pos * 3, pos * 3, 0, 0)
#     if pos < 170:
#         pos -= 85
#         return (0, 255 - pos * 3, pos * 3, 0)
#     pos -= 170
#     return (pos * 3, 0, 255 - pos * 3, 0)


# def color_chase(color, wait):
#     for i in range(num_pixels):
#         pixels[i] = color
#         time.sleep(wait)
#         pixels.show()
#     time.sleep(0.5)


# def rainbow_cycle(wait):
#     for j in range(255):
#         for i in range(num_pixels):
#             rc_index = (i * 256 // num_pixels) + j
#             pixels[i] = colorwheel(rc_index & 255)
#         pixels.show()
#         time.sleep(wait)


# RED = (255, 0, 0, 0)
# YELLOW = (255, 150, 0, 0)
# GREEN = (0, 255, 0, 0)
# CYAN = (0, 255, 255, 0)
# BLUE = (0, 0, 255, 0)
# PURPLE = (180, 0, 255, 0)

# while True:
#     pixels.fill(RED)
#     pixels.show()
#     # Increase or decrease to change the speed of the solid color change.
#     time.sleep(1)
#     pixels.fill(GREEN)
#     pixels.show()
#     time.sleep(1)
#     pixels.fill(BLUE)
#     pixels.show()
#     time.sleep(1)

#     color_chase(RED, 0.1)  # Increase the number to slow down the color chase
#     color_chase(YELLOW, 0.1)
#     color_chase(GREEN, 0.1)
#     color_chase(CYAN, 0.1)
#     color_chase(BLUE, 0.1)
#     color_chase(PURPLE, 0.1)

#     rainbow_cycle(0)  # Increase the number to slow down the rainbow