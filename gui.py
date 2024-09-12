import tkinter as tk
from recording import start_recording, stop_recording, replay_actions, save_actions, load_actions

class MousePad:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Automation Tool")
        self.root.geometry("600x400")
        
        # Status Label to indicate current state
        self.status_label = tk.Label(root, text="Status: Ready")
        self.status_label.pack(pady=10)

        # Add an input field for the loop count
        self.loop_count_label = tk.Label(root, text="Loop Count:")
        self.loop_count_label.pack(pady=5)

        self.loop_count_var = tk.IntVar(value=1)  # Default loop count to 1
        self.loop_count_entry = tk.Entry(root, textvariable=self.loop_count_var)
        self.loop_count_entry.pack(pady=5)

        # GUI Buttons
        self.start_button = tk.Button(root, text="Start Recording (Ctrl+R)", command=self.start_recording)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop Recording (Ctrl+S)", command=self.stop_recording)
        self.stop_button.pack(pady=10)

        self.play_button = tk.Button(root, text="Play Actions (Ctrl+P)", command=self.play_with_loops)
        self.play_button.pack(pady=10)

        self.save_button = tk.Button(root, text="Save Actions (Ctrl+Q)", command=save_actions)
        self.save_button.pack(pady=10)

        self.load_button = tk.Button(root, text="Load Actions (Ctrl+L)", command=load_actions)
        self.load_button.pack(pady=10)

        # Action Count Label to show how many actions have been recorded
        self.action_count_label = tk.Label(root, text="Actions Recorded: 0")
        self.action_count_label.pack(pady=20)

    def start_recording(self):
        """Start recording and update the status label."""
        self.update_status("Recording...")
        start_recording()
        self.update_action_count()  # Reset action count when starting fresh

    def stop_recording(self):
        """Stop recording and update the status label."""
        stop_recording()
        self.update_status("Recording Stopped")
        self.update_action_count()

    def play_with_loops(self):
        """Replay recorded actions based on the loop count input."""
        loop_count = self.loop_count_var.get()
        replay_actions(loop_count)
        self.update_status(f"Playing {loop_count} Loops")

    def update_status(self, message):
        """Update the status label with the current status."""
        self.status_label.config(text=f"Status: {message}")

    def update_action_count(self, count=None):
        """Update the action count label."""
        if count is None:
            from recording import recorded_actions
            count = len(recorded_actions)
        self.action_count_label.config(text=f"Actions Recorded: {count}")