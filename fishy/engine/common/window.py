import logging
from enum import Enum
from typing import List

import cv2
import imutils

from fishy.engine.common import window_server
from fishy.engine.common.window_server import WindowServer, Status
from fishy.helper import helper


class WindowClient:
    clients: List['WindowClient'] = []

    def __init__(self, crop=None, color=None, scale=None, show_name=None):
        """
        create a window instance with these pre process
        :param crop: [x1,y1,x2,y2] array defining the boundaries to crop
        :param color: color to use example cv2.COLOR_RGB2HSV
        :param scale: scaling the window
        """
        self.color = color
        self.crop = crop
        self.scale = scale
        self.show_name = show_name
        self.showing = False

        if len(WindowClient.clients) == 0:
            window_server.start()
        WindowClient.clients.append(self)

    def __del__(self):
        WindowClient.clients.remove(self)
        if len(WindowClient.clients) == 0:
            window_server.stop()

    def get_capture(self):
        """
        copies the recorded screen and then pre processes its
        :return: game window image
        """
        if WindowServer.status == Status.CRASHED:
            return None

        if not window_server.screen_ready():
            logging.info("waiting fors screen...")
            helper.wait_until(window_server.screen_ready)
            logging.info("screen ready, continuing...")

        temp_img = WindowServer.Screen

        if temp_img is None:
            return None

        if self.color is not None:
            temp_img = cv2.cvtColor(temp_img, self.color)

        if self.crop is not None:
            temp_img = temp_img[self.crop[1]:self.crop[3], self.crop[0]:self.crop[2]]

        if self.scale is not None:
            temp_img = cv2.resize(temp_img, (self.scale[0], self.scale[1]), interpolation=cv2.INTER_AREA)

        return temp_img

    def processed_image(self, func=None):
        """
        processes the image using the function provided
        :param func: function to process image
        :return: processed image
        """
        if WindowServer.status == Status.CRASHED:
            return None

        if func is None:
            return self.get_capture()
        else:
            return func(self.get_capture())

    def show(self, resize=None, func=None, ready_img=None):
        """
        Displays the processed image for debugging purposes
        :param ready_img: send ready image, just show the `ready_img` directly
        :param name: unique name for the image, used to create a new window
        :param resize: scale the image to make small images more visible
        :param func: function to process the image
        """
        if WindowServer.status == Status.CRASHED:
            return

        if not self.show_name:
            logging.warning("You need to assign a name first")
            return

        if ready_img is None:
            img = self.processed_image(func)

            if resize is not None:
                img = imutils.resize(img, width=resize)
        else:
            img = ready_img
        cv2.imshow(self.show_name, img)

        self.showing = True
