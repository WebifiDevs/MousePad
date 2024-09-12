import pyautogui
import time
import json
import threading
import tkinter as tk
from pynput import mouse, keyboard
from emergency_stop import start_emergency_listener, stop_emergency_listener, stop_replay

# Global variables to track recording state and actions
is_recording = False
recorded_actions = []
start_time = 0
mouse_listener = None
keyboard_listener = None
recording_area = None  # Define the area as (x1, y1, x2, y2)
last_mouse_move_time = 0  # For throttling mouse move events
mouse_move_interval = 0.1  # Record mouse moves every 0.1 seconds
click_count = 0  # To track the number of clicks for visual markers
record_mouse_moves = False  # Set to True to record mouse movements

def record_action(action_type, **kwargs):
    """Record an action with its type, timestamp, and additional data."""
    action = {
        "type": action_type,
        "timestamp": time.time(),
        **kwargs
    }
    recorded_actions.append(action)

def is_within_area(x, y):
    """Check if the coordinates are within the recording area."""
    if recording_area is None:
        return True
    x1, y1, x2, y2 = recording_area
    return x1 <= x <= x2 and y1 <= y <= y2

def draw_marker(x, y, click_number):
    """Draw a red dot at the click position and keep it visible with a number."""
    def create_overlay():
        overlay_window = tk.Tk()
        overlay_window.overrideredirect(True)
        overlay_window.attributes("-topmost", True)
        overlay_window.attributes("-transparentcolor", "white")
        overlay_window.geometry(f"{overlay_window.winfo_screenwidth()}x{overlay_window.winfo_screenheight()}+0+0")
        overlay_canvas = tk.Canvas(overlay_window, bg="white", highlightthickness=0)
        overlay_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw the red marker with a number
        marker_radius = 10
        overlay_canvas.create_oval(x - marker_radius, y - marker_radius,
                                   x + marker_radius, y + marker_radius,
                                   fill="red", outline="red")
        overlay_canvas.create_text(x, y - 20, text=str(click_number), fill="white", font=("Helvetica", 12, "bold"))
        overlay_canvas.update()
        
        # Keep the overlay visible for a short time
        time.sleep(0.5)
        overlay_window.destroy()
    
    # Run the overlay in a separate thread
    threading.Thread(target=create_overlay).start()

def start_recording(update_gui_state=None, update_log=None):
    """Start recording mouse and keyboard actions."""
    global is_recording, start_time, recorded_actions, mouse_listener, keyboard_listener, click_count
    is_recording = True
    start_time = time.time()
    recorded_actions = []
    click_count = 0  # Reset click count

    # Capture the starting position of the mouse
    start_x, start_y = pyautogui.position()
    record_action("start", x=start_x, y=start_y)
    if update_log:
        update_log(f"Recording started at position: {start_x}, {start_y}")
    else:
        print(f"Recording started at position: {start_x}, {start_y}")
    if update_gui_state:
        update_gui_state(is_recording=True)

    # Start mouse listener
    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    mouse_listener.start()

    # Start keyboard listener
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()

def stop_recording(update_gui_state=None, update_log=None):
    """Stop recording mouse and keyboard actions."""
    global is_recording, mouse_listener, keyboard_listener
    is_recording = False

    # Capture the ending position of the mouse
    end_x, end_y = pyautogui.position()
    record_action("end", x=end_x, y=end_y)

    # Stop the listeners to prevent them from running in the background
    if mouse_listener is not None:
        mouse_listener.stop()
        mouse_listener = None
    if keyboard_listener is not None:
        keyboard_listener.stop()
        keyboard_listener = None

    if update_log:
        update_log(f"Recording stopped at position: {end_x}, {end_y}. Total actions recorded: {len(recorded_actions)}")
    else:
        print(f"Recording stopped at position: {end_x}, {end_y}. Total actions recorded: {len(recorded_actions)}")
    if update_gui_state:
        update_gui_state(is_recording=False)

def on_move(x, y):
    """Handle mouse move events."""
    global is_recording, start_time, last_mouse_move_time
    if is_recording and is_within_area(x, y) and record_mouse_moves:
        current_time = time.time()
        if current_time - last_mouse_move_time >= mouse_move_interval:
            delay = current_time - start_time
            record_action("move", x=x, y=y, delay=delay)
            start_time = current_time
            last_mouse_move_time = current_time

def on_click(x, y, button, pressed):
    """Handle mouse click events."""
    global is_recording, start_time, click_count
    if is_recording and is_within_area(x, y):
        delay = time.time() - start_time
        button_name = button.name  # 'left', 'right', 'middle'
        if pressed:
            record_action("button_press", x=x, y=y, button=button_name, delay=delay)
            click_count += 1
            draw_marker(x, y, click_count)
        else:
            record_action("button_release", x=x, y=y, button=button_name, delay=delay)
        start_time = time.time()

def on_scroll(x, y, dx, dy):
    """Handle mouse scroll events."""
    global is_recording, start_time
    if is_recording and is_within_area(x, y):
        delay = time.time() - start_time
        record_action("scroll", x=x, y=y, dx=dx, dy=dy, delay=delay)
        start_time = time.time()

def on_press(key):
    """Handle keyboard key press events."""
    global is_recording, start_time
    if is_recording:
        delay = time.time() - start_time
        try:
            key_name = key.char if hasattr(key, 'char') else key.name
        except AttributeError:
            key_name = str(key)
        record_action("key_press", key=key_name, delay=delay)
        start_time = time.time()

def on_release(key):
    """Handle keyboard key release events."""
    global is_recording, start_time
    if is_recording:
        delay = time.time() - start_time
        try:
            key_name = key.char if hasattr(key, 'char') else key.name
        except AttributeError:
            key_name = str(key)
        record_action("key_release", key=key_name, delay=delay)
        start_time = time.time()

def replay_actions(loop_count=1, speed_factor=1.0, update_log=None):
    """Replay the recorded actions with an optional loop count and speed factor."""
    if update_log:
        update_log(f"Replaying {len(recorded_actions)} actions, {loop_count} times at {speed_factor}x speed...")
    else:
        print(f"Replaying {len(recorded_actions)} actions, {loop_count} times at {speed_factor}x speed...")
    for _ in range(loop_count):
        if not recorded_actions:
            if update_log:
                update_log("No actions to replay.")
            else:
                print("No actions to replay.")
            return
        # Start emergency listener
        start_emergency_listener()
        for i, action in enumerate(recorded_actions):
            # Check for emergency stop
            if stop_replay:
                if update_log:
                    update_log("Replay stopped by user.")
                else:
                    print("Replay stopped by user.")
                break
            # Calculate time to wait before executing this action
            if i == 0:
                time_to_wait = 0
            else:
                time_to_wait = (action['timestamp'] - recorded_actions[i - 1]['timestamp']) / speed_factor
            time.sleep(time_to_wait)
            # Execute the action based on its type
            if action['type'] == "start":
                pyautogui.moveTo(action['x'], action['y'], duration=0.1)
            elif action['type'] == "move":
                pyautogui.moveTo(action['x'], action['y'])
            elif action['type'] == "button_press":
                pyautogui.mouseDown(x=action['x'], y=action['y'], button=action['button'])
            elif action['type'] == "button_release":
                pyautogui.mouseUp(x=action['x'], y=action['y'], button=action['button'])
            elif action['type'] == "scroll":
                pyautogui.scroll(int(action['dy']), x=action['x'], y=action['y'])
            elif action['type'] == "key_press":
                pyautogui.keyDown(action['key'])
            elif action['type'] == "key_release":
                pyautogui.keyUp(action['key'])
            elif action['type'] == "end":
                pyautogui.moveTo(action['x'], action['y'], duration=0.1)
            # Add other action types as needed
        # Stop emergency listener after each loop
        stop_emergency_listener()
        if stop_replay:
            break
        if update_log:
            update_log("Replay iteration finished.")
        else:
            print("Replay iteration finished.")
    if update_log:
        update_log("Replay finished.")
    else:
        print("Replay finished.")
    # Ensure emergency listener is stopped
    stop_emergency_listener()

def save_actions(filename="actions.json"):
    """Save recorded actions to a JSON file."""
    with open(filename, "w") as f:
        json.dump(recorded_actions, f)
    print(f"Actions saved to {filename}")

def load_actions(filename="actions.json"):
    """Load actions from a JSON file."""
    global recorded_actions
    with open(filename, "r") as f:
        recorded_actions = json.load(f)
    print(f"Loaded {len(recorded_actions)} actions from {filename}")

def get_recorded_actions():
    """Get the list of recorded actions."""
    return recorded_actions

def set_recorded_actions(actions):
    """Set the list of recorded actions."""
    global recorded_actions
    recorded_actions = actions
