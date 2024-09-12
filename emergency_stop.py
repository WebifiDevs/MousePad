# emergency_stop.py

from pynput import keyboard

stop_replay = False
_listener = None

def on_press(key):
    global stop_replay
    if key == keyboard.Key.esc:
        stop_replay = True
        return False  # Stop the listener

def start_emergency_listener():
    global _listener, stop_replay
    stop_replay = False
    _listener = keyboard.Listener(on_press=on_press)
    _listener.start()

def stop_emergency_listener():
    global _listener
    if _listener is not None:
        _listener.stop()
        _listener = None
