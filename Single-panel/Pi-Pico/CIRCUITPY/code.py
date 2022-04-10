
import time
import board
import digitalio
import rotaryio
import neopixel
import adafruit_fancyled.adafruit_fancyled as fancy

## UPDATED ATTEMPT AT THE RGB WORK BUT THIS TIME USING HSV AND FANCYLED
#  -- HSV is like fancy.CHSV(0.1, 0.2, 0.3)  (all numbers 0-1)
#  -- where 0.1 is in the "Hue" space and can actually take on any non-integer
#  -- 0.2 is in the saturation space, determines how white the color is
#  -- 0.3 is in the value space and should determine darkness... 
#  == https://learn.adafruit.com/fancyled-library-for-circuitpython/colors 


# set button for encoder
button = digitalio.DigitalInOut(board.GP20)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP
button_state = None  # tracks the state of the button so that one press is only one press
button_switch = 1 # sets whether to move in columns or rows thru color matrices (False is across columns (single row))

pixel_pin = board.GP17
num_pixels = 6

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False)
                           # pixel_order=(1, 0, 2, 3))

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
StepSat = 0.05  # twenty total
thisSat = 0.5    # full is 1
newSat = thisSat # start at initial
## VALUE (Brightness)
StepValue = 0.05
thisValue = 0.1  # full is 1
newValue = thisValue
## BUTTONS [1=hue; 2=sat; 3=val]
## SET COLOR
thisCol = fancy.CHSV(thisHue, thisSat, thisValue)
## ========================================= ## 

encoder = rotaryio.IncrementalEncoder(board.GP18, board.GP19)
last_position = encoder.position
turn_dir = 1   # plus one or minus one, necessary for moving up and down a single column of matrix

# confusing loop because newcol refers to column and thisCol refers to color
while True:
    position = encoder.position

    if last_position is None or position != last_position:
        print(position)
    
    ## =========== HUE BUTTON ============ #
    if button_switch == 1:  # modify new col 
        if position < last_position: # move to lower column
            newHue = newHue - StepHue
            # if newHue < HSVmin:  # commented out bc hue can be any color (periodic around 1.0)
            #     newHue = HSVmin   # loop around
            # print(newHue)
        elif position > last_position: # move to higher column
            newHue = newHue + StepHue
            # if newHue > HSVmax:  # commented out bc hue can be any color (periodic around 1.0)
            #     newHue = HSVmax  # loop around 
            # print(newHue)
        elif last_position == position:
            newHue = newHue
            # print(newHue)
        # print to strip 
        thisCol = fancy.CHSV(newHue, newSat, newValue)
        pixels.fill(thisCol.pack())
        pixels.show()
        last_position = position 

    ## =========== SAT BUTTON ============ #
    elif button_switch == 2:  # modify new row
        if position < last_position: # move to lower column
            if turn_dir == 1:  # then move new row in the opposite direction
                rowDirectionMultiplier = rowDirectionMultiplier * -1
            turn_dir = -1
            newSat = newSat + (StepSat*rowDirectionMultiplier)  # multiplier starts positive, so adding moves to higher (lower-number) rows
            if newSat < HSVmin:
                rowDirectionMultiplier = 1.0  # hit floor, start counting up
                newSat = HSVmin + (StepSat*rowDirectionMultiplier) 
            elif newSat > HSVmax:
                rowDirectionMultiplier = -1.0  # hit ceiling, start counting down
                newSat = HSVmax + (StepSat*rowDirectionMultiplier)
            print("this row:"); print(newSat)
        elif position > last_position: # move to higher column
            if turn_dir == -1:  # then move new row in the opposite direction
                rowDirectionMultiplier = rowDirectionMultiplier * -1.0
            turn_dir = 1
            newSat = newSat + (StepSat*rowDirectionMultiplier)
            if newSat < HSVmin:
                rowDirectionMultiplier = 1.0  # hit floor, start counting up
                newSat = HSVmin + (StepSat*rowDirectionMultiplier) 
            elif newSat > HSVmax:
                rowDirectionMultiplier = -1.0  # hit ceiling, start counting down
                newSat = HSVmax + (StepSat*rowDirectionMultiplier)
            print("this row:"); print(newSat)
        elif last_position == position:
            newSat = newSat
            # print(newcol)
        # print to strip
        thisCol = fancy.CHSV(newHue, newSat, newValue)
        pixels.fill(thisCol.pack())
        pixels.show()
        last_position = position

    ## =========== VALUE BUTTON ============ #
    elif button_switch == 3:  # modify new row
        if position < last_position: # move to lower column
            if turn_dir == 1:  # then move new row in the opposite direction
                rowDirectionMultiplier = rowDirectionMultiplier * -1
            turn_dir = -1
            newValue = newValue + (StepValue*rowDirectionMultiplier)  # multiplier starts positive, so adding moves to higher (lower-number) rows
            if newValue < HSVmin:
                rowDirectionMultiplier = 1.0  # hit floor, start counting up
                newValue = HSVmin + (StepValue*rowDirectionMultiplier) 
            elif newValue > HSVmax:
                rowDirectionMultiplier = -1.0  # hit ceiling, start counting down
                newValue = HSVmax + (StepValue*rowDirectionMultiplier)
            print("this row:"); print(newValue)
        elif position > last_position: # move to higher column
            if turn_dir == -1:  # then move new row in the opposite direction
                rowDirectionMultiplier = rowDirectionMultiplier * -1.0
            turn_dir = 1
            newValue = newValue + (StepValue*rowDirectionMultiplier)
            if newValue < HSVmin:
                rowDirectionMultiplier = 1.0  # hit floor, start counting up
                newValue = HSVmin + (StepValue*rowDirectionMultiplier) 
            elif newValue > HSVmax:
                rowDirectionMultiplier = -1.0  # hit ceiling, start counting down
                newValue = HSVmax + (StepValue*rowDirectionMultiplier)
            print("this row:"); print(newValue)
        elif last_position == position:
            newValue = newValue
            # print(newcol)
        # print to strip
        thisCol = fancy.CHSV(newHue, newSat, newValue)
        pixels.fill(thisCol.pack())
        pixels.show()
        last_position = position



    # now the button
    if not button.value and button_state is None:  # button state is ready to be pressed
        button_state = "pressed"
    if button.value and button_state == "pressed": # once it's pressed the button state goes to off
        # print(button.pull)
        print(button_state)
        button_state = None
        button_switch = button_switch + 1
        if button_switch > 3:
            button_switch = 1
        time.sleep(0.1)






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