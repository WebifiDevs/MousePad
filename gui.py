import customtkinter as ctk
from recording import start_recording, stop_recording, save_actions, replay_actions, load_actions, get_recorded_actions, set_recorded_actions
import threading
import tkinter.messagebox as tkmessagebox
import tkinter.ttk as ttk
from tkinter import simpledialog
from pynput import keyboard

class MousePad(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set up window
        self.title("MousePad")
        self.geometry("375x600")
        self.config(bg='#262E3F')  # Dark background

        # Define button colors
        self.button_color = "#308C65"  # Standard button color
        self.recording_color = "#E53E3E"  # Recording button color

        # Configure grid layout for centering elements
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # State management
        self.current_frame = None
        self.is_recording = False  # Track whether recording is ongoing
        self.log_text = None  # Placeholder for the log widget
        self.play_button = None  # Placeholder for the play button
        self.replay_speed = 1.0  # Initialize replay speed

        # Display the initial menu state
        self.show_menu_state()

        # Register keyboard shortcuts
        self.register_shortcuts()

        # Handle window closing to stop listeners
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handle application closing."""
        # Stop the hotkey listener
        if hasattr(self, 'hotkey_listener') and self.hotkey_listener is not None:
            self.hotkey_listener.stop()
        self.destroy()

    def register_shortcuts(self):
        """Register global keyboard shortcuts using pynput."""
        # Define hotkey actions
        def on_activate_r():
            print('Ctrl+R pressed')
            self.start_recording()

        def on_activate_s():
            print('Ctrl+S pressed')
            self.stop_recording()

        def on_activate_p():
            print('Ctrl+P pressed')
            self.replay_recording()

        def on_activate_q():
            print('Ctrl+Q pressed')
            self.save_actions_via_shortcut()

        def on_activate_l():
            print('Ctrl+L pressed')
            self.load_actions_via_shortcut()

        self.hotkey_listener = keyboard.GlobalHotKeys({
            '<ctrl>+r': on_activate_r,
            '<ctrl>+s': on_activate_s,
            '<ctrl>+p': on_activate_p,
            '<ctrl>+q': on_activate_q,
            '<ctrl>+l': on_activate_l
        })
        self.hotkey_listener.start()
        print("Keyboard shortcuts registered: Ctrl+R (Record), Ctrl+S (Stop), Ctrl+P (Play), Ctrl+Q (Save), Ctrl+L (Load)")

    def save_actions_via_shortcut(self):
        """Save actions via shortcut."""
        filename = simpledialog.askstring("Save Recording", "Enter filename to save recording:")
        if filename:
            save_actions(filename)
            self.update_log(f"Recording saved as {filename}")
        else:
            self.update_log("Save canceled.")

    def load_actions_via_shortcut(self):
        """Load actions via shortcut."""
        filename = simpledialog.askstring("Load Recording", "Enter filename to load recording:")
        if filename:
            load_actions(filename)
            self.update_log(f"Loaded recording from {filename}.")
            self.show_init_recording_state()
        else:
            self.update_log("Load canceled.")

    def clear_frame(self):
        """Clear the current frame for switching between states."""
        if self.current_frame is not None:
            self.current_frame.destroy()

    def ensure_log_text(self):
        """Ensure that the log_text widget exists."""
        if not self.log_text:
            self.log_text = ctk.CTkTextbox(self, height=10, state="normal", wrap="none", fg_color='#262E3F', text_color="white")
            self.log_text.pack_forget()

    def show_menu_state(self):
        """Frame 1: Display the main menu with buttons for Record, Load Recording, and How it works."""
        self.clear_frame()
        self.current_frame = ctk.CTkFrame(self, fg_color='#262E3F')
        self.current_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Configure grid layout for the buttons
        self.current_frame.grid_columnconfigure(0, weight=1)

        # Title and Buttons
        button_font = ("Nunito", 18)
        button_padding = 10

        record_button = ctk.CTkButton(self.current_frame, text="Record", font=button_font, height=50, width=200, fg_color=self.button_color, command=self.show_init_recording_state)
        record_button.grid(row=0, column=0, pady=button_padding, padx=20, sticky="ew")

        load_button = ctk.CTkButton(self.current_frame, text="Load Recording", font=button_font, height=50, width=200, fg_color=self.button_color, command=self.show_load_state)
        load_button.grid(row=1, column=0, pady=button_padding, padx=20, sticky="ew")

        how_button = ctk.CTkButton(self.current_frame, text="How it works", font=button_font, height=50, width=200, fg_color=self.button_color, command=self.show_how_state)
        how_button.grid(row=2, column=0, pady=button_padding, padx=20, sticky="ew")

    def show_init_recording_state(self):
        """Frame 2: Initial state where user can click the button to start recording."""
        self.clear_frame()
        self.current_frame = ctk.CTkFrame(self, fg_color='#262E3F')
        self.current_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Configure grid layout for the frame
        self.current_frame.grid_columnconfigure(0, weight=1)

        # Log area (Text widget)
        self.log_text = ctk.CTkTextbox(self.current_frame, height=10, state="normal", wrap="none", fg_color='#262E3F', text_color="white")
        self.log_text.grid(row=1, column=0, pady=10, padx=10, sticky="ew")
        self.log_text.insert("end", "Ready to record...\n")
        self.log_text.configure(state="disabled")

        # Start and Play buttons
        self.record_button = ctk.CTkButton(self.current_frame, text="Start", font=("Nunito", 18), height=50, fg_color=self.button_color, command=self.toggle_recording)
        self.record_button.grid(row=2, column=0, pady=10, padx=20, sticky="ew")

        self.play_button = ctk.CTkButton(self.current_frame, text="Play", font=("Nunito", 18), height=50, fg_color=self.button_color, command=self.replay_recording)
        self.play_button.grid(row=3, column=0, pady=10, padx=20, sticky="ew")

        # Speed adjustment slider
        speed_label = ctk.CTkLabel(self.current_frame, text="Replay Speed:", font=("Nunito", 14), text_color="white")
        speed_label.grid(row=4, column=0, pady=(10, 0), padx=20, sticky="ew")

        self.speed_slider = ctk.CTkSlider(self.current_frame, from_=0.5, to=2.0, number_of_steps=15, command=self.update_speed)
        self.speed_slider.set(1.0)  # Default speed is 1.0
        self.speed_slider.grid(row=5, column=0, pady=5, padx=20, sticky="ew")

        # Add a button to access the action list
        action_list_button = ctk.CTkButton(self.current_frame, text="Edit Actions", font=("Nunito", 18), height=50, fg_color=self.button_color, command=self.show_action_list)
        action_list_button.grid(row=6, column=0, pady=10, padx=20, sticky="ew")

        # Add a button to select recording area
        area_button = ctk.CTkButton(self.current_frame, text="Set Recording Area", font=("Nunito", 18), height=50, fg_color=self.button_color, command=self.select_recording_area)
        area_button.grid(row=7, column=0, pady=10, padx=20, sticky="ew")

    def toggle_recording(self):
        """Toggle between starting and stopping recording."""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        """Start recording and update the status."""
        self.is_recording = True
        self.update_log("Recording started...")
        self.record_button.configure(fg_color=self.recording_color, text="Stop")
        # Start recording in a separate thread to prevent GUI freezing
        threading.Thread(target=start_recording, args=(self.update_gui_state, self.update_log)).start()

    def stop_recording(self):
        """Stop recording and update the status."""
        self.is_recording = False
        # Stop recording in a separate thread to prevent GUI freezing
        threading.Thread(target=stop_recording, args=(self.update_gui_state, self.update_log)).start()
        self.update_log("Recording stopped.")
        self.record_button.configure(fg_color=self.button_color, text="Start")
        self.show_save_state()

    def replay_recording(self):
        """Replay the recorded actions."""
        # Ask for confirmation before replaying
        if tkmessagebox.askyesno("Confirm Replay", "Are you sure you want to replay the recorded actions? This may interfere with your control of the system. Press 'Esc' to stop replay."):
            self.update_log("Replaying recorded actions...")
            # Start replay in a separate thread to prevent GUI freezing
            threading.Thread(target=replay_actions, args=(1, self.replay_speed, self.update_log)).start()
        else:
            self.update_log("Replay canceled.")

    def update_speed(self, value):
        """Update the replay speed based on slider value."""
        self.replay_speed = float(value)
        self.update_log(f"Replay speed set to {self.replay_speed:.2f}x")

    def update_log(self, message):
        """Update the log area with new messages."""
        self.ensure_log_text()
        if self.log_text:
            self.log_text.configure(state="normal")
            self.log_text.insert("end", f"{message}\n")
            self.log_text.yview_moveto(1)  # Scroll to the bottom
            self.log_text.configure(state="disabled")

    def update_gui_state(self, is_recording):
        """Update the GUI state based on recording status."""
        self.is_recording = is_recording
        if is_recording:
            self.record_button.configure(fg_color=self.recording_color, text="Stop Recording")
        else:
            self.record_button.configure(fg_color=self.button_color, text="Start Recording")

    def show_save_state(self):
        """Prompt the user to save the recording."""
        filename = simpledialog.askstring("Save Recording", "Enter filename to save recording:")
        if filename:
            save_actions(filename)
            self.update_log(f"Recording saved as {filename}")
        else:
            self.update_log("Save canceled.")
        self.show_menu_state()

    def show_load_state(self):
        """Prompt the user to load a recording."""
        filename = simpledialog.askstring("Load Recording", "Enter filename to load recording:")
        if filename:
            load_actions(filename)
            self.update_log(f"Loaded recording from {filename}.")
            self.show_init_recording_state()  # Navigate to playback state
        else:
            self.update_log("Load canceled.")

    def show_how_state(self):
        """Display how it works information."""
        self.clear_frame()
        self.current_frame = ctk.CTkFrame(self, fg_color='#262E3F')
        self.current_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.current_frame.grid_columnconfigure(0, weight=1)

        how_text = ("Welcome to MousePad!\n\n"
                    "Instructions:\n"
                    "1. Click 'Record' to start recording your mouse and keyboard actions.\n"
                    "2. Perform the actions you want to automate.\n"
                    "3. Click 'Stop' to end the recording.\n"
                    "4. Save your recording for future use.\n"
                    "5. Load a recording and click 'Play' to replay the actions.\n\n"
                    "Press 'Esc' during replay to stop it immediately.\n\n"
                    "Keyboard Shortcuts:\n"
                    "- Ctrl+R: Start Recording\n"
                    "- Ctrl+S: Stop Recording\n"
                    "- Ctrl+P: Play Recording\n"
                    "- Ctrl+Q: Save Recording\n"
                    "- Ctrl+L: Load Recording")

        how_label = ctk.CTkLabel(self.current_frame, text=how_text, font=("Nunito", 14), text_color="white", justify="left")
        how_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        back_button = ctk.CTkButton(self.current_frame, text="Back", font=("Nunito", 18), height=50, fg_color=self.button_color, command=self.show_menu_state)
        back_button.grid(row=1, column=0, pady=10, padx=20, sticky="ew")

    def show_action_list(self):
        """Display the list of recorded actions for editing."""
        self.clear_frame()
        self.current_frame = ctk.CTkFrame(self, fg_color='#262E3F')
        self.current_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.current_frame.grid_columnconfigure(0, weight=1)
        self.current_frame.grid_rowconfigure(0, weight=1)

        # Treeview to display actions
        columns = ("Type", "Details")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#262E3F", foreground="white", fieldbackground="#262E3F", font=("Nunito", 12))
        style.configure("Treeview.Heading", background="#262E3F", foreground="white", font=("Nunito", 12, "bold"))

        self.action_tree = ttk.Treeview(self.current_frame, columns=columns, show='headings', style="Treeview")
        self.action_tree.heading("Type", text="Type")
        self.action_tree.heading("Details", text="Details")
        self.action_tree.grid(row=0, column=0, sticky="nsew")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.current_frame, orient="vertical", command=self.action_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.action_tree.configure(yscroll=scrollbar.set)

        # Populate the treeview
        actions = get_recorded_actions()
        for idx, action in enumerate(actions):
            details = ', '.join(f"{k}: {v}" for k, v in action.items() if k != 'type' and k != 'timestamp')
            self.action_tree.insert('', 'end', iid=str(idx), values=(action['type'], details))

        # Buttons to delete or edit actions
        button_frame = ctk.CTkFrame(self.current_frame, fg_color='#262E3F')
        button_frame.grid(row=1, column=0, pady=10, sticky="ew", columnspan=2)

        delete_button = ctk.CTkButton(button_frame, text="Delete Action", font=("Nunito", 14), fg_color="red", command=self.delete_action)
        delete_button.pack(side='left', padx=5)

        back_button = ctk.CTkButton(button_frame, text="Back", font=("Nunito", 14), fg_color=self.button_color, command=self.show_init_recording_state)
        back_button.pack(side='right', padx=5)

    def delete_action(self):
        """Delete the selected action from the recorded actions."""
        selected_item = self.action_tree.selection()
        if selected_item:
            idx = int(selected_item[0])
            actions = get_recorded_actions()
            del actions[idx]
            set_recorded_actions(actions)
            self.update_log(f"Deleted action at index {idx}")
            self.show_action_list()  # Refresh the list
        else:
            self.update_log("No action selected to delete.")

    def select_recording_area(self):
        """Allow the user to select a screen area for recording."""
        # For demonstration, we'll use a fixed area
        # Implementing a draggable rectangle is complex and beyond this scope
        from recording import recording_area
        recording_area = (100, 100, 800, 600)
        self.update_log(f"Recording area set to {recording_area}")

# Run the application
if __name__ == "__main__":
    app = MousePad()
    app.mainloop()
