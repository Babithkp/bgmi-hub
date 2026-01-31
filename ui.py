# ui.py
from nt import read
import warnings
warnings.filterwarnings("ignore", message=".*pin_memory.*")

import threading
import time
import re
import tkinter as tk
from tkinter import ttk
import webbrowser

import easyocr
import mss
import numpy as np
import cv2

from matcher import match_player
import app_state

# =============================
# GLOBAL STATE
# =============================
ocr_running = False
show_preview = True
selected_monitor_index = 1

# UI Positions
TeamShortLogoTop = 57
TeamShortLogoLeft = 10
TeamShortLogoWidth = 100
TeamShortLogoHeight = 32

TeamLogoTop = 866
TeamLogoLeft = 644
TeamLogoSize = 70

PlayerImgTop = 897
PlayerImgLeft = 1280
PlayerImgSize = 174

send_logo_position = False

OVERLAY_URL = "http://127.0.0.1:3000"

OCR_REGION = {
    "top": 850,
    "left": 710,
    "width": 350,
    "height": 100,
}

PREVIEW_PADDING = 120
reader = None

# =============================
# OCR INIT (CPU ONLY)
# =============================
def init_reader():
    global reader
    reader = easyocr.Reader(["en"], gpu=False)
    print("OCR ENGINE INITIALIZED (CPU ONLY)")

# =============================
# TEXT PARSER
# =============================
def parse_hud_text(lines):
    tokens = []
    for line in lines:
        clean = line.strip()
        if len(clean) >= 3 and "/" not in clean:
            tokens.append(clean)
    return tokens

# =============================
# OCR THREAD
# =============================
def ocr_loop():
    global ocr_running, send_logo_position

    with mss.mss() as sct:
        monitors = sct.monitors

        while ocr_running:
            try:
                monitor = monitors[selected_monitor_index]
                img = np.array(sct.grab(monitor))

                x, y, w, h = (
                    OCR_REGION["left"],
                    OCR_REGION["top"],
                    OCR_REGION["width"],
                    OCR_REGION["height"],
                )

                crop = img[y:y+h, x:x+w]
                raw_text = reader.readtext(crop, detail=0)
                tokens = parse_hud_text(raw_text)

                logo_payload = {}
                if send_logo_position:
                    logo_payload = {
                        "TeamShortLogoTop": TeamShortLogoTop,
                        "TeamShortLogoLeft": TeamShortLogoLeft,
                        "TeamShortLogoWidth": TeamShortLogoWidth,
                        "TeamShortLogoHeight": TeamShortLogoHeight,
                        "TeamLogoTop": TeamLogoTop,
                        "TeamLogoLeft": TeamLogoLeft,
                        "TeamLogoSize": TeamLogoSize,
                        "PlayerImgTop": PlayerImgTop,
                        "PlayerImgLeft": PlayerImgLeft,
                        "PlayerImgSize": PlayerImgSize,
                    }
                    send_logo_position = False

                match = match_player(tokens)
                if match:
                    app_state.CURRENT_MATCH = {
                        **match,
                        "ui_position": logo_payload,
                    }

                if show_preview:
                    px1 = max(0, x - PREVIEW_PADDING)
                    py1 = max(0, y - PREVIEW_PADDING)
                    px2 = min(img.shape[1], x + w + PREVIEW_PADDING)
                    py2 = min(img.shape[0], y + h + PREVIEW_PADDING)

                    preview = img[py1:py2, px1:px2].copy()
                    cv2.rectangle(
                        preview,
                        (x - px1, y - py1),
                        (x - px1 + w, y - py1 + h),
                        (0, 255, 0),
                        2,
                    )
                    cv2.imshow("OCR Preview", preview)
                    cv2.waitKey(1)
                else:
                    cv2.destroyAllWindows()

            except Exception as e:
                print("OCR ERROR:", e)

            time.sleep(1)

        cv2.destroyAllWindows()

# =============================
# UI CALLBACKS
# =============================
def start_ocr():
    global ocr_running
    if ocr_running:
        return
    ocr_running = True
    threading.Thread(target=ocr_loop, daemon=True).start()
    print("OCR STARTED")

def stop_ocr():
    global ocr_running
    ocr_running = False
    print("OCR STOPPED")

def update_region():
    OCR_REGION["top"] = int(top_var.get())
    OCR_REGION["left"] = int(left_var.get())
    OCR_REGION["width"] = int(width_var.get())
    OCR_REGION["height"] = int(height_var.get())
    print("UPDATED OCR REGION:", OCR_REGION)

def toggle_preview():
    global show_preview
    show_preview = preview_var.get()

def open_overlay():
    webbrowser.open(OVERLAY_URL + "/overlay")

def select_monitor(*_):
    global selected_monitor_index
    selected_monitor_index = int(monitor_var.get())

def apply_logo_position():
    global TeamShortLogoTop, TeamShortLogoLeft, TeamShortLogoWidth
    global TeamShortLogoHeight, TeamLogoTop, TeamLogoLeft
    global TeamLogoSize, PlayerImgTop, PlayerImgLeft, PlayerImgSize
    global send_logo_position

    TeamShortLogoTop = int(short_logo_top_var.get())
    TeamShortLogoLeft = int(short_logo_left_var.get())
    TeamShortLogoWidth = int(short_logo_width_var.get())
    TeamShortLogoHeight = int(short_logo_height_var.get())

    TeamLogoTop = int(team_logo_top_var.get())
    TeamLogoLeft = int(team_logo_left_var.get())
    TeamLogoSize = int(team_logo_size_var.get())

    PlayerImgTop = int(player_img_top_var.get())
    PlayerImgLeft = int(player_img_left_var.get())
    PlayerImgSize = int(player_img_size_var.get())

    send_logo_position = True
    print("UI POSITIONS UPDATED")

# =============================
# UI WINDOW
# =============================
def start_ui():
    global top_var, left_var, width_var, height_var
    global short_logo_top_var, short_logo_left_var, short_logo_width_var, short_logo_height_var
    global team_logo_top_var, team_logo_left_var, team_logo_size_var
    global player_img_top_var, player_img_left_var, player_img_size_var
    global preview_var, monitor_var

    root = tk.Tk()
    root.title("BGMI OCR Overlay Controller")
    root.geometry("440x720")

    # --- Scrollable container ---
    canvas = tk.Canvas(root, borderwidth=0)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    frame = ttk.Frame(canvas, padding=10)
    canvas_window = canvas.create_window((0, 0), window=frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame.bind("<Configure>", on_frame_configure)

    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)

    canvas.bind("<Configure>", on_canvas_configure)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    Overlay_Page = tk.StringVar(value=OVERLAY_URL + "/overlay")
    ttk.Label(frame, text="Overlay Page URL").pack(anchor="w")
    ttk.Entry(frame, textvariable=Overlay_Page,state="readonly").pack(fill="x")

    ttk.Label(frame, text="Select Monitor").pack(anchor="w")
    monitor_var = tk.StringVar(value="1")
    with mss.mss() as sct:
        ttk.Combobox(
            frame,
            values=[str(i) for i in range(1, len(sct.monitors))],
            textvariable=monitor_var,
            state="readonly",
        ).pack(fill="x")
    monitor_var.trace_add("write", select_monitor)

    ttk.Label(frame, text="OCR Region").pack(anchor="w", pady=(10, 0))
    top_var = tk.StringVar(value=str(OCR_REGION["top"]))
    left_var = tk.StringVar(value=str(OCR_REGION["left"]))
    width_var = tk.StringVar(value=str(OCR_REGION["width"]))
    height_var = tk.StringVar(value=str(OCR_REGION["height"]))

    for lbl, var in [("Top", top_var), ("Left", left_var), ("Width", width_var), ("Height", height_var)]:
        ttk.Label(frame, text=lbl).pack(anchor="w")
        ttk.Entry(frame, textvariable=var).pack(fill="x")

    ttk.Button(frame, text="Apply OCR Region", command=update_region).pack(fill="x", pady=4)

    preview_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(frame, text="Show OCR Preview", variable=preview_var, command=toggle_preview).pack(anchor="w")

    ttk.Button(frame, text="Start OCR", command=start_ocr).pack(fill="x", pady=4)
    ttk.Button(frame, text="Stop OCR", command=stop_ocr).pack(fill="x")

    ttk.Label(frame, text="UI Positions").pack(anchor="w", pady=(10, 0))

    def field(label, var):
        ttk.Label(frame, text=label).pack(anchor="w")
        ttk.Entry(frame, textvariable=var).pack(fill="x")

    short_logo_top_var = tk.StringVar(value="57")
    short_logo_left_var = tk.StringVar(value="10")
    short_logo_width_var = tk.StringVar(value="100")
    short_logo_height_var = tk.StringVar(value="32")

    team_logo_top_var = tk.StringVar(value="866")
    team_logo_left_var = tk.StringVar(value="644")
    team_logo_size_var = tk.StringVar(value="70")

    player_img_top_var = tk.StringVar(value="897")
    player_img_left_var = tk.StringVar(value="1280")
    player_img_size_var = tk.StringVar(value="174")

    field("Team Short Logo Top", short_logo_top_var)
    field("Team Short Logo Left", short_logo_left_var)
    field("Team Short Logo Width", short_logo_width_var)
    field("Team Short Logo Height", short_logo_height_var)

    field("Team Logo Top", team_logo_top_var)
    field("Team Logo Left", team_logo_left_var)
    field("Team Logo Size", team_logo_size_var)

    field("Player Image Top", player_img_top_var)
    field("Player Image Left", player_img_left_var)
    field("Player Image Size", player_img_size_var)

    ttk.Button(frame, text="Apply UI Position", command=apply_logo_position).pack(fill="x", pady=6)

    init_reader()
    root.mainloop()