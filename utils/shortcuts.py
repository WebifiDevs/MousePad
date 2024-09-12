import keyboard
from recording import start_recording, stop_recording, replay_actions, save_actions, load_actions

def register_shortcuts():
    """Register global keyboard shortcuts to control the mouse automation tool."""
    
    # Start Recording (Ctrl+R)
    keyboard.add_hotkey('ctrl+r', start_recording)
    
    # Stop Recording (Ctrl+S)
    keyboard.add_hotkey('ctrl+s', stop_recording)
    
    # Play Recorded Actions (Ctrl+P)
    keyboard.add_hotkey('ctrl+p', lambda: replay_actions(loop_count=1))  # Default loop count 1
    
    # Save Recorded Actions (Ctrl+Q)
    keyboard.add_hotkey('ctrl+q', save_actions)
    
    # Load Recorded Actions (Ctrl+L)
    keyboard.add_hotkey('ctrl+l', load_actions)
    
    print("Keyboard shortcuts registered: Ctrl+R (Record), Ctrl+S (Stop), Ctrl+P (Play), Ctrl+Q (Save), Ctrl+L (Load)")

