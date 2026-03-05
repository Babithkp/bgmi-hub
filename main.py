import os
import sys
import threading

if hasattr(sys, "_MEIPASS"):
    torch_lib_path = os.path.join(sys._MEIPASS, "torch", "lib")
    os.add_dll_directory(torch_lib_path)
from server import app
from ui import start_ui
from matcher import load_teams


def start_server():
    print("Starting overlay server on http://127.0.0.1:3000")
    app.run(host="127.0.0.1", port=3000, debug=False, use_reloader=False)


if __name__ == "__main__":
    load_teams()  # load team DB once

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    start_ui()
