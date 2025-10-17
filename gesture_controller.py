# ui.py
import cv2
import mediapipe as mp
import math
import threading
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import tkinter as tk
from tkinter import ttk

# ----------- Audio Setup -----------
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
vol_range = volume.GetVolumeRange()
min_vol = vol_range[0]
max_vol = vol_range[1]

# ----------- Hand Detection Setup -----------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# ----------- Global Variables -----------
cap = None
running = False
vol_perc = 0
vol_bar = 400

# ----------- Functions -----------

def start_camera():
    global cap, running
    if not running:
        cap = cv2.VideoCapture(0)
        running = True
        threading.Thread(target=update_frame, daemon=True).start()

def stop_camera():
    global cap, running
    running = False
    if cap:
        cap.release()
    cv2.destroyAllWindows()

def update_frame():
    global vol_perc, vol_bar
    while running:
        success, img = cap.read()
        if not success:
            continue
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                lm_list = []
                for id, lm in enumerate(hand_landmarks.landmark):
                    h, w, _ = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append((id, cx, cy))

                if lm_list:
                    x1, y1 = lm_list[4][1], lm_list[4][2]  # Thumb tip
                    x2, y2 = lm_list[8][1], lm_list[8][2]  # Index tip
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                    # Draw visuals
                    cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
                    cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
                    cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
                    cv2.circle(img, (cx, cy), 8, (0, 255, 0), cv2.FILLED)

                    # Distance to volume
                    length = math.hypot(x2 - x1, y2 - y1)
                    vol = min_vol + (length / 200) * (max_vol - min_vol)
                    vol = max(min(vol, max_vol), min_vol)
                    volume.SetMasterVolumeLevel(vol, None)

                    # Volume percentage for UI
                    vol_perc = int((vol - min_vol) / (max_vol - min_vol) * 100)
                    vol_bar = 400 - int((vol_perc / 100) * 300)

        # Draw color-changing volume bar
        if vol_perc < 33:
            color = (0, 255, 0)  # Green
        elif vol_perc < 66:
            color = (0, 255, 255)  # Yellow
        else:
            color = (0, 0, 255)  # Red

        cv2.rectangle(img, (50, 100), (85, 400), (255, 255, 255), 2)
        cv2.rectangle(img, (50, vol_bar), (85, 400), color, cv2.FILLED)
        cv2.putText(img, f'{vol_perc} %', (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(img, "Move thumb & index to control volume", (100, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

        cv2.imshow("Hand Gesture Volume Controller", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_camera()
            break

# ----------- GUI Setup -----------

root = tk.Tk()
root.title("Hand Gesture Volume Controller")
root.geometry("400x250")
root.resizable(False, False)

# Title Label
title_label = ttk.Label(root, text="Hand Gesture Volume Controller", font=("Helvetica", 14, "bold"))
title_label.pack(pady=10)

# Instructions
instr_label = ttk.Label(root, text="Instructions:\n- Click Start to open webcam\n- Move thumb & index to adjust volume\n- Click Stop to close webcam", font=("Helvetica", 10))
instr_label.pack(pady=10)

# Volume display
vol_label = ttk.Label(root, text="Volume: 0%", font=("Helvetica", 12, "bold"))
vol_label.pack(pady=5)

# Update the volume label periodically
def update_vol_label():
    vol_label.config(text=f"Volume: {vol_perc}%")
    root.after(200, update_vol_label)

update_vol_label()

# Start / Stop buttons
start_btn = ttk.Button(root, text="Start Webcam", command=start_camera)
start_btn.pack(pady=5)

stop_btn = ttk.Button(root, text="Stop Webcam", command=stop_camera)
stop_btn.pack(pady=5)

root.mainloop()
