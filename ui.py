import tkinter as tk
from threading import Thread
from gesture_controller import HandGestureVolumeController

controller = None
running = False

def start_controller():
    global controller, running
    if not running:
        running = True
        controller = HandGestureVolumeController()
        Thread(target=controller.run).start()

def stop_controller():
    global running
    running = False
    controller.cap.release()
    tk.messagebox.showinfo("Stopped", "Gesture Volume Controller stopped successfully.")

root = tk.Tk()
root.title("Gesture Volume Controller")
root.geometry("350x200")
root.config(bg="#222")

label = tk.Label(root, text="🎵 Hand Gesture Volume Controller", bg="#222", fg="white", font=("Arial", 12, "bold"))
label.pack(pady=20)

start_btn = tk.Button(root, text="Start", bg="#4CAF50", fg="white", width=12, command=start_controller)
start_btn.pack(pady=10)

stop_btn = tk.Button(root, text="Stop", bg="#F44336", fg="white", width=12, command=stop_controller)
stop_btn.pack(pady=5)

root.mainloop()
