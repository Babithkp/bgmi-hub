# ocr_engine.py
import time
import threading
import mss
import numpy as np
import easyocr
from matcher import match_player

CURRENT_MATCH = None
ocr_running = False
reader = easyocr.Reader(['en'], gpu=False)

def ocr_loop():
    global CURRENT_MATCH, ocr_running

    with mss.mss() as sct:
        monitor = sct.monitors[1]

        while ocr_running:
            img = np.array(sct.grab(monitor))
            crop = img[850:950, 710:1060]  # your region

            raw_text = reader.readtext(crop, detail=0)

            match = match_player(raw_text)
            if match:
                CURRENT_MATCH = match

            time.sleep(1)

def start_ocr():
    global ocr_running
    if not ocr_running:
        ocr_running = True
        threading.Thread(target=ocr_loop, daemon=True).start()

def stop_ocr():
    global ocr_running
    ocr_running = False