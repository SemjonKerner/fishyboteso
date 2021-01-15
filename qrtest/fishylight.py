import sys
import cv2
from win32gui import GetWindowRect, FindWindow
import numpy
from PIL import ImageGrab
import time
import keyboard
"""d3dshot is a faster alternative to ImageGrab
   https://pypi.org/project/d3dshot/ """
#import d3dshot

laststate = 0
#cap = d3dshot.create(capture_output="numpy")
dur = time.time()
qrCodeDetector = cv2.QRCodeDetector()

while True:
    """get the window and crop the top left corner"""
    try:
        window = GetWindowRect(FindWindow(None, "Elder Scrolls Online"))
        windowcrop = (window[0],window[1],int(window[2]/4),int(window[3]/4))
        temp_screen = numpy.array(ImageGrab.grab(bbox=windowcrop))
    except OSError:
        print("ImageGrab failed")
        exit()
    except:
        print("ESO not started")
        exit()

    #temp_screen = cap.screenshot(region=windowcrop)
    temp_screen = cv2.cvtColor(temp_screen, cv2.COLOR_BGR2RGB)

    """decode the qr from the cropped screenshot"""
    decodedText, points, _ = qrCodeDetector.detectAndDecode(temp_screen)

    """statemachine for fishylight - use as PoC"""
    if points is not None:
        print("QR Code Content: " + decodedText)
        """split CSV: last value is Chalutier state"""
        state = decodedText.split(",")[-1]
        """qr code is start or stop"""
        try:
            state = int(state)
        except ValueError:
            time.sleep(1)
            continue

        if time.time()-dur > 2.0:
            laststate=-1
        """2: start fishing, 7: reel in"""
        if state != laststate and (state == 2 or state == 7):
            print("\npress e")
            keyboard.press_and_release('e')
            laststate = state
            dur = time.time()
            if state == 2:
                time.sleep(1)
        """8: loot, 9: inv full (try to loot)"""
        if state != laststate and (state == 8 or state == 9):
            print("\npress r")
            keyboard.press_and_release('r')
            laststate = state
            dur = time.time()
            time.sleep(1)
    else:
        print("QR code not detected")

    sys.stdout.flush()

    """delay to allow ctrl+c"""
    time.sleep(0.03)