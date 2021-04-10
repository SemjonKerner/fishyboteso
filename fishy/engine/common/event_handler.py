import logging
import time
import threading
import queue

from fishy.engine import SemiFisherEngine
from fishy.engine.fullautofisher.engine import FullAuto


class EngineEventHandler:
    def __init__(self, gui_ref):
        self.event_handler_running = True
        self.event = queue.Queue()

        self.semi_fisher_engine = SemiFisherEngine(gui_ref)
        self.full_fisher_engine = FullAuto(gui_ref)

    def start_event_handler(self, gui):
        while self.event_handler_running and gui._thread in threading.enumerate():
            while not self.event.empty():
                event = self.event.get()
                event()
            time.sleep(0.1)

    def toggle_semifisher(self):
        self.event.put(self.semi_fisher_engine.toggle_start)

    def toggle_fullfisher(self):
        self.event.put(self.full_fisher_engine.toggle_start)

    def check_pixel_val(self):
        def func():
            if self.semi_fisher_engine.start:
                self.semi_fisher_engine.show_pixel_vals()
            else:
                logging.debug("Start the engine first before running this command")

        self.event.put(func)

    def quit(self):
        def func():
            self.semi_fisher_engine.start = False
            self.event_handler_running = False
            gui._destroyed = True

        self.event.put(func)
