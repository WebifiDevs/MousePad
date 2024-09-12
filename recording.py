import pyautogui
import time
import json
import threading
import tkinter as tk
from pynput.mouse import Listener as MouseListener

# Global variables to track recording state and actions
is_recording = False
recorded_actions = []
start_time = 0  # Initialize start_time globally
listener = None  # Declare listener as a global variable to control its lifecycle
click_count = 0  # To track the number of clicks for visual markers

def record_action(action_type, x, y, button=None, delay=None, double_click=False):
    """Record an action (move, click, etc.) with coordinates, button, and delay."""
    action = {
        "type": action_type,
        "x": x,
        "y": y,
        "button": button,
        "delay": delay,
        "double_click": double_click  # Add flag to handle double clicks
    }
    recorded_actions.append(action)

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
        
        # Keep the overlay visible
        overlay_window.mainloop()
    
    # Run the overlay in a separate thread
    threading.Thread(target=create_overlay).start()

def start_recording(update_gui_state=None, update_log=None):
    """Start recording mouse actions."""
    global is_recording, start_time, recorded_actions, listener, click_count
    is_recording = True
    start_time = time.time()  # Properly initialize start_time
    recorded_actions = []  # Clear previous actions
    click_count = 0  # Reset click count

    # Capture the starting position of the mouse
    start_x, start_y = pyautogui.position()
    record_action("start", start_x, start_y)
    if update_log:
        update_log(f"Recording started at position: {start_x}, {start_y}")
    if update_gui_state:
        update_gui_state(is_recording=True)

    # Start listening to mouse events
    listener = MouseListener(on_click=on_click)
    listener.start()

def stop_recording(update_gui_state=None, update_log=None):
    """Stop recording mouse actions."""
    global is_recording, listener
    is_recording = False

    # Capture the ending position of the mouse
    end_x, end_y = pyautogui.position()
    record_action("end", end_x, end_y)

    # Stop the listener to prevent it from running in the background
    if listener is not None:
        listener.stop()
        listener = None

    if update_log:
        update_log(f"Recording stopped at position: {end_x}, {end_y}. Total actions recorded: {len(recorded_actions)}")
    if update_gui_state:
        update_gui_state(is_recording=False)

def on_click(x, y, button, pressed):
    """Handle mouse click events."""
    global start_time, click_count
    if is_recording and pressed:  # Only record mouse button press events, not release
        delay = time.time() - start_time
        click_count += 1  # Increment click count for visual markers

        # Check if this is a double-click event
        double_click = False
        if click_count > 1 and (time.time() - start_time) < 0.3:  # Less than 0.3s between clicks = double-click
            double_click = True

        record_action("click", x, y, button=str(button), delay=delay, double_click=double_click)
        draw_marker(x, y, click_count)  # Display visual marker for each click with numbering
        start_time = time.time()  # Reset start time after each action
        print(f"Mouse clicked at ({x}, {y}) with button {button} - Click {click_count} - Double-click: {double_click}")

def replay_actions(loop_count=1, update_log=None):
    """Replay the recorded actions with an optional loop count."""
    if update_log:
        update_log(f"Replaying {len(recorded_actions)} actions, {loop_count} times...")
    for _ in range(loop_count):
        for action in recorded_actions:
            if action["type"] == "start":
                print(f"Moving to start position: {action['x']}, {action['y']}")
                pyautogui.moveTo(action["x"], action["y"], duration=0.3)  # Add duration for smoother movement
            elif action["type"] == "click":
                print(f"Clicking at {action['x']}, {action['y']} with button {action['button']}")
                pyautogui.moveTo(action["x"], action["y"], duration=0.2)  # Smoother transition to click position
                if action["button"] == "Button.left":
                    if action["double_click"]:
                        pyautogui.doubleClick(action["x"], action["y"])  # Double click
                    else:
                        pyautogui.click(action["x"], action["y"])  # Single click
                elif action["button"] == "Button.right":
                    pyautogui.click(action["x"], action["y"], button='right')  # Right click
            elif action["type"] == "end":
                print(f"Moving to end position: {action['x']}, {action['y']}")
                pyautogui.moveTo(action["x"], action["y"], duration=0.3)  # Add duration for smoother movement
            time.sleep(action["delay"] if action["delay"] else 0.2)  # Adjusted delay for smoother playback
    if update_log:
        update_log("Replay finished.")

def save_actions(filename="actions/actions.json"):
    """Save recorded actions to a JSON file."""
    with open(filename, "w") as f:
        json.dump(recorded_actions, f)
    print(f"Actions saved to {filename}")

def load_actions(filename="actions/actions.json"):
    """Load actions from a JSON file."""
    global recorded_actions
    with open(filename, "r") as f:
        recorded_actions = json.load(f)
    print(f"Loaded {len(recorded_actions)} actions from {filename}")