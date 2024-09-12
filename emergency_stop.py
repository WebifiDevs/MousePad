# emergency_stop.py

from pynput import keyboard

# Global variable to track if the replay should stop
stop_replay = False
emergency_listener = None

def on_press(key):
    global stop_replay
    if key == keyboard.Key.esc:
        stop_replay = True
        return False  # Stop the listener

def start_emergency_listener():
    """Start the emergency stop keyboard listener."""
    global emergency_listener, stop_replay
    stop_replay = False  # Reset the flag at the start
    emergency_listener = keyboard.Listener(on_press=on_press)
    emergency_listener.start()

def stop_emergency_listener():
    """Stop the emergency stop keyboard listener."""
    global emergency_listener
    if emergency_listener is not None:
        emergency_listener.stop()
        emergency_listener = None
