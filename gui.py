# gui.py

import customtkinter as ctk
from tkinter import simpledialog, filedialog, ttk
from tkinter import messagebox as tkmessagebox
import threading
import tkinter
import queue
import os

import keyboard  # Using the 'keyboard' module for keyboard events

import recording  # Importing the entire module

class MousePad(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set up window
        self.title("MousePad")
        self.geometry("500x700")
        self.config(bg='#262E3F')  # Dark background

        # Define button colors
        self.button_color = "#308C65"  # Standard button color
        self.recording_color = "#E53E3E"  # Recording button color

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # State management
        self.current_frame = None
        self.is_recording = False
        self.log_text = None
        self.play_button = None
        self.replay_speed = 1.0

        # Default keyboard shortcuts
        self.shortcuts = {
            'record': 'ctrl+r',
            'stop': 'ctrl+s',
            'play': 'ctrl+p',
            'save': 'ctrl+q',
            'load': 'ctrl+l'
        }

        # List to keep track of registered hotkeys
        self.hotkey_handlers = []

        # Create a queue for thread-safe GUI updates
        self.log_queue = queue.Queue()

        # Display the initial menu state
        self.show_menu_state()

        # Register keyboard shortcuts
        self.register_shortcuts()

        # Handle window closing to stop listeners
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start processing the log queue
        self.process_log_queue()

    def on_closing(self):
        """Handle application closing."""
        # Unhook existing hotkeys
        if hasattr(self, 'hotkey_handlers'):
            for handler in self.hotkey_handlers:
                keyboard.remove_hotkey(handler)
        # Stop recording if active
        if self.is_recording:
            recording.stop_recording()
        self.destroy()

    def register_shortcuts(self):
        """Register global keyboard shortcuts using the 'keyboard' module."""
        # Unhook existing hotkeys
        if hasattr(self, 'hotkey_handlers'):
            for handler in self.hotkey_handlers:
                keyboard.remove_hotkey(handler)
        else:
            self.hotkey_handlers = []

        # Define hotkey actions
        try:
            self.hotkey_handlers.append(keyboard.add_hotkey(self.shortcuts['record'], lambda: self.start_recording()))
            self.hotkey_handlers.append(keyboard.add_hotkey(self.shortcuts['stop'], lambda: self.stop_recording()))
            self.hotkey_handlers.append(keyboard.add_hotkey(self.shortcuts['play'], lambda: self.replay_recording()))
            self.hotkey_handlers.append(keyboard.add_hotkey(self.shortcuts['save'], lambda: self.save_actions_via_shortcut()))
            self.hotkey_handlers.append(keyboard.add_hotkey(self.shortcuts['load'], lambda: self.load_actions_via_shortcut()))
            print(f"Keyboard shortcuts registered: {self.shortcuts}")
            self.update_log(f"Keyboard shortcuts registered: {self.shortcuts}")
        except Exception as e:
            self.update_log(f"Failed to register global hotkeys: {e}")

    def save_actions_via_shortcut(self):
        """Save actions via shortcut."""
        self.save_recording()

    def load_actions_via_shortcut(self):
        """Load actions via shortcut."""
        self.show_load_state()

    def clear_frame(self):
        """Clear the current frame for switching between states."""
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None
            self.log_text = None  # Reset log_text when frame is cleared
            self.update_idletasks()  # Process any pending events

    def ensure_log_text(self):
        """Ensure that the log_text widget exists."""
        if not self.log_text and self.current_frame and hasattr(self.current_frame, 'log_text_placeholder'):
            self.log_text = ctk.CTkTextbox(
                self.current_frame,
                height=10,
                state="normal",
                wrap="none",
                fg_color='#262E3F',
                text_color="white"
            )
            self.log_text.grid(row=1, column=0, pady=10, padx=10, sticky="nsew")
            self.log_text.configure(state="disabled")

    def show_menu_state(self):
        """Display the main menu with buttons."""
        self.clear_frame()
        self.current_frame = ctk.CTkFrame(self, fg_color='#262E3F')
        self.current_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Configure grid layout
        self.current_frame.grid_columnconfigure(0, weight=1)

        # Buttons
        button_font = ("Nunito", 18)
        button_padding = 10

        record_button = ctk.CTkButton(
            self.current_frame, text="Record", font=button_font, height=50,
            width=200, fg_color=self.button_color, command=self.show_init_recording_state)
        record_button.grid(row=0, column=0, pady=button_padding, padx=20, sticky="ew")

        load_button = ctk.CTkButton(
            self.current_frame, text="Load Recording", font=button_font, height=50,
            width=200, fg_color=self.button_color, command=self.show_load_state)
        load_button.grid(row=1, column=0, pady=button_padding, padx=20, sticky="ew")

        how_button = ctk.CTkButton(
            self.current_frame, text="How it works", font=button_font, height=50,
            width=200, fg_color=self.button_color, command=self.show_how_state)
        how_button.grid(row=2, column=0, pady=button_padding, padx=20, sticky="ew")

        settings_button = ctk.CTkButton(
            self.current_frame, text="Settings", font=button_font, height=50,
            width=200, fg_color=self.button_color, command=self.show_settings)
        settings_button.grid(row=3, column=0, pady=button_padding, padx=20, sticky="ew")

    def show_init_recording_state(self):
        """Initial state where user can start recording."""
        self.clear_frame()
        self.current_frame = ctk.CTkFrame(self, fg_color='#262E3F')
        self.current_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Configure grid layout
        self.current_frame.grid_columnconfigure(0, weight=1)
        self.current_frame.grid_rowconfigure(0, weight=1)

        # Log area
        self.log_text = ctk.CTkTextbox(
            self.current_frame, height=10, state="normal", wrap="none",
            fg_color='#262E3F', text_color="white")
        self.log_text.grid(row=1, column=0, pady=10, padx=10, sticky="nsew")
        self.log_text.insert("end", "Ready to record...\n")
        self.log_text.configure(state="disabled")

        # Start and Play buttons
        self.record_button = ctk.CTkButton(
            self.current_frame, text="Start", font=("Nunito", 18), height=50,
            fg_color=self.button_color, command=self.toggle_recording)
        self.record_button.grid(row=2, column=0, pady=10, padx=20, sticky="ew")

        self.play_button = ctk.CTkButton(
            self.current_frame, text="Play", font=("Nunito", 18), height=50,
            fg_color=self.button_color, command=self.replay_recording)
        self.play_button.grid(row=3, column=0, pady=10, padx=20, sticky="ew")

        # Save button (initially disabled)
        self.save_button = ctk.CTkButton(
            self.current_frame, text="Save Recording", font=("Nunito", 18), height=50,
            fg_color=self.button_color, command=self.save_recording, state="disabled")
        self.save_button.grid(row=4, column=0, pady=10, padx=20, sticky="ew")

        # Speed adjustment slider
        speed_label = ctk.CTkLabel(
            self.current_frame, text="Replay Speed:", font=("Nunito", 14), text_color="white")
        speed_label.grid(row=5, column=0, pady=(10, 0), padx=20, sticky="ew")

        self.speed_slider = ctk.CTkSlider(
            self.current_frame, from_=0.5, to=2.0, number_of_steps=15, command=self.update_speed)
        self.speed_slider.set(1.0)
        self.speed_slider.grid(row=6, column=0, pady=5, padx=20, sticky="ew")

        # Option to record mouse movements
        self.mouse_move_var = ctk.IntVar(value=1)
        mouse_move_checkbox = ctk.CTkCheckBox(
            self.current_frame, text="Record Mouse Movements", variable=self.mouse_move_var,
            command=self.toggle_mouse_moves)
        mouse_move_checkbox.grid(row=7, column=0, pady=10, padx=20, sticky="ew")

        # Button to access the action list
        action_list_button = ctk.CTkButton(
            self.current_frame, text="Edit Actions", font=("Nunito", 18), height=50,
            fg_color=self.button_color, command=self.show_action_list)
        action_list_button.grid(row=8, column=0, pady=10, padx=20, sticky="ew")

        # Button to select recording area
        area_button = ctk.CTkButton(
            self.current_frame, text="Set Recording Area", font=("Nunito", 18), height=50,
            fg_color=self.button_color, command=self.select_recording_area)
        area_button.grid(row=9, column=0, pady=10, padx=20, sticky="ew")

        self.current_frame.log_text_placeholder = True

    def toggle_mouse_moves(self):
        """Toggle recording of mouse movements."""
        value = bool(self.mouse_move_var.get())
        recording.set_record_mouse_moves(value)
        self.update_log(f"Record Mouse Movements set to {value}")

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
        self.save_button.configure(state="disabled")  # Disable save button during recording
        # Start recording in a separate thread
        threading.Thread(target=recording.start_recording, args=(self.update_gui_state, self.update_log)).start()

    def stop_recording(self):
        """Stop recording and update the status."""
        self.is_recording = False
        # Stop recording in a separate thread
        threading.Thread(target=recording.stop_recording, args=(self.update_gui_state, self.update_log)).start()
        self.update_log("Recording stopped.")
        self.record_button.configure(fg_color=self.button_color, text="Start")
        self.save_button.configure(state="normal")  # Enable save button after recording

    def save_recording(self):
        """Save the recorded actions to a file."""
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            try:
                recording.save_actions(filename)
                self.update_log(f"Recording saved as {filename}")
            except Exception as e:
                self.update_log(f"Error saving recording: {e}")
        else:
            self.update_log("Save canceled.")

    def replay_recording(self):
        """Replay the recorded actions."""
        # Ask for confirmation before replaying
        if tkmessagebox.askyesno("Confirm Replay", "Are you sure you want to replay the recorded actions? This may interfere with your control of the system. Press 'Esc' to stop replay."):
            self.update_log("Replaying recorded actions...")
            # Start replay in a separate thread
            threading.Thread(target=recording.replay_actions, args=(1, self.replay_speed, self.update_log)).start()
        else:
            self.update_log("Replay canceled.")

    def update_speed(self, value):
        """Update the replay speed based on slider value."""
        self.replay_speed = float(value)
        self.update_log(f"Replay speed set to {self.replay_speed:.2f}x")

    def update_log(self, message):
        """Update the log area with new messages."""
        self.log_queue.put(message)

    def process_log_queue(self):
        """Process messages in the log queue."""
        if self.log_text and self.log_text.winfo_exists():
            while not self.log_queue.empty():
                message = self.log_queue.get()
                try:
                    self.log_text.configure(state="normal")
                    self.log_text.insert("end", f"{message}\n")
                    self.log_text.yview_moveto(1)  # Scroll to the bottom
                    self.log_text.configure(state="disabled")
                except Exception as e:
                    print(f"Error updating log: {e}")
        self.after(100, self.process_log_queue)

    def update_gui_state(self, is_recording):
        """Update the GUI state based on recording status."""
        self.is_recording = is_recording
        def update():
            if is_recording:
                self.record_button.configure(fg_color=self.recording_color, text="Stop Recording")
            else:
                self.record_button.configure(fg_color=self.button_color, text="Start Recording")
        self.after(0, update)

    def show_load_state(self):
        """Prompt the user to load a recording."""
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            try:
                recording.load_actions(filename)
                self.update_log(f"Loaded recording from {filename}.")
                self.show_init_recording_state()  # Navigate to playback state
                self.save_button.configure(state="normal")  # Enable save button if a recording is loaded
            except Exception as e:
                self.update_log(f"Error loading recording: {e}")
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
                    "1. Click 'Start' to begin recording your mouse and keyboard actions.\n"
                    "2. Perform the actions you want to automate.\n"
                    "3. Click 'Stop' to end the recording.\n"
                    "4. Click 'Save Recording' to save your recording for future use.\n"
                    "5. Load a recording and click 'Play' to replay the actions.\n\n"
                    "Press 'Esc' during replay to stop it immediately.\n\n"
                    "Keyboard Shortcuts:\n"
                    f"- Record: {self.shortcuts['record']}\n"
                    f"- Stop: {self.shortcuts['stop']}\n"
                    f"- Play: {self.shortcuts['play']}\n"
                    f"- Save: {self.shortcuts['save']}\n"
                    f"- Load: {self.shortcuts['load']}")

        how_label = ctk.CTkLabel(
            self.current_frame, text=how_text, font=("Nunito", 14),
            text_color="white", justify="left")
        how_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        back_button = ctk.CTkButton(
            self.current_frame, text="Back", font=("Nunito", 18), height=50,
            fg_color=self.button_color, command=self.show_menu_state)
        back_button.grid(row=1, column=0, pady=10, padx=20, sticky="ew")

    def show_settings(self):
        """Display the settings window for customizing keyboard shortcuts."""
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.grab_set()

        settings_window.grid_columnconfigure(1, weight=1)

        row = 0
        entries = {}

        for action, shortcut in self.shortcuts.items():
            label = ctk.CTkLabel(
                settings_window, text=f"{action.capitalize()} Shortcut:", font=("Nunito", 12))
            label.grid(row=row, column=0, padx=10, pady=5, sticky="e")
            entry = ctk.CTkEntry(settings_window, font=("Nunito", 12))
            entry.insert(0, shortcut)
            entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
            entries[action] = entry
            row += 1

        def save_settings():
            # Update the shortcuts
            for action, entry in entries.items():
                self.shortcuts[action] = entry.get()
            self.register_shortcuts()
            self.update_log("Keyboard shortcuts updated.")
            settings_window.destroy()

        save_button = ctk.CTkButton(settings_window, text="Save", command=save_settings)
        save_button.grid(row=row, column=0, columnspan=2, pady=10)

    def show_action_list(self):
        """Display the list of recorded actions for editing."""
        self.clear_frame()
        self.current_frame = ctk.CTkFrame(self, fg_color='#262E3F')
        self.current_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.current_frame.grid_columnconfigure(0, weight=1)
        self.current_frame.grid_rowconfigure(0, weight=1)

        # Use ttk.Treeview for interactive action list
        columns = ("Index", "Type", "Details")
        style = ttk.Style()
        style.configure("Treeview", background="#262E3F", foreground="white",
                        fieldbackground="#262E3F", font=("Nunito", 12))
        style.configure("Treeview.Heading", background="#262E3F", foreground="white",
                        font=("Nunito", 12, "bold"))
        style.map('Treeview', background=[('selected', '#3A3F4B')])

        self.action_tree = ttk.Treeview(
            self.current_frame, columns=columns, show='headings')
        self.action_tree.heading("Index", text="Index")
        self.action_tree.heading("Type", text="Type")
        self.action_tree.heading("Details", text="Details")
        self.action_tree.column("Index", width=50)
        self.action_tree.column("Type", width=100)
        self.action_tree.column("Details", width=300)
        self.action_tree.grid(row=0, column=0, sticky="nsew")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self.current_frame, orient="vertical", command=self.action_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.action_tree.configure(yscroll=scrollbar.set)

        # Populate the treeview
        actions = recording.get_recorded_actions()
        for idx, action in enumerate(actions):
            details = ', '.join(f"{k}: {v}" for k, v in action.items() if k != 'type' and k != 'timestamp')
            self.action_tree.insert('', 'end', iid=str(idx), values=(idx, action['type'], details))

        # Buttons to edit or delete actions
        button_frame = ctk.CTkFrame(self.current_frame, fg_color='#262E3F')
        button_frame.grid(row=1, column=0, pady=10, sticky="ew", columnspan=2)

        edit_button = ctk.CTkButton(
            button_frame, text="Edit Action", font=("Nunito", 14),
            fg_color=self.button_color, command=self.edit_action)
        edit_button.pack(side='left', padx=5)

        delete_button = ctk.CTkButton(
            button_frame, text="Delete Action", font=("Nunito", 14),
            fg_color="red", command=self.delete_action)
        delete_button.pack(side='left', padx=5)

        back_button = ctk.CTkButton(
            button_frame, text="Back", font=("Nunito", 14),
            fg_color=self.button_color, command=self.show_init_recording_state)
        back_button.pack(side='right', padx=5)

    def edit_action(self):
        """Edit the selected action."""
        selected_item = self.action_tree.selection()
        if selected_item:
            idx = int(selected_item[0])
            actions = recording.get_recorded_actions()
            action = actions[idx]

            # Open a dialog to edit the action
            edit_window = ctk.CTkToplevel(self)
            edit_window.title("Edit Action")
            edit_window.geometry("400x400")
            edit_window.grab_set()

            # Display action details
            row = 0
            entries = {}
            for key, value in action.items():
                if key == 'timestamp':
                    continue  # Skip timestamp
                label = ctk.CTkLabel(edit_window, text=key, font=("Nunito", 12))
                label.grid(row=row, column=0, padx=10, pady=5, sticky="e")
                entry = ctk.CTkEntry(edit_window, font=("Nunito", 12))
                entry.insert(0, str(value))
                entry.grid(row=row, column=1, padx=10, pady=5, sticky="w")
                entries[key] = entry
                row += 1

            def save_changes():
                # Update the action with new values
                for key, entry in entries.items():
                    try:
                        if key in ['x', 'y', 'dx', 'dy']:
                            action[key] = float(entry.get())
                        elif key == 'delay':
                            action[key] = float(entry.get())
                        else:
                            action[key] = entry.get()
                    except ValueError:
                        self.update_log(f"Invalid value for {key}.")
                        return
                recording.set_recorded_actions(actions)
                self.update_log(f"Action at index {idx} updated.")
                edit_window.destroy()
                self.show_action_list()  # Refresh the list

            save_button = ctk.CTkButton(edit_window, text="Save", command=save_changes)
            save_button.grid(row=row, column=0, columnspan=2, pady=10)

        else:
            self.update_log("No action selected to edit.")

    def delete_action(self):
        """Delete the selected action from the recorded actions."""
        selected_item = self.action_tree.selection()
        if selected_item:
            idx = int(selected_item[0])
            actions = recording.get_recorded_actions()
            if 0 <= idx < len(actions):
                if tkmessagebox.askyesno("Confirm Delete", f"Are you sure you want to delete action at index {idx}?"):
                    del actions[idx]
                    recording.set_recorded_actions(actions)
                    self.update_log(f"Deleted action at index {idx}")
                    self.show_action_list()  # Refresh the list
                else:
                    self.update_log("Delete action canceled.")
            else:
                self.update_log("Invalid action index.")
        else:
            self.update_log("No action selected to delete.")

    def select_recording_area(self):
        """Allow the user to select a screen area for recording."""
        # For simplicity, we'll use predefined options
        area_options = {
            "Full Screen": (0, 0, self.winfo_screenwidth(), self.winfo_screenheight()),
            "Top-Left Quarter": (0, 0, self.winfo_screenwidth() // 2, self.winfo_screenheight() // 2),
            "Custom Area": None  # Implement custom selection if needed
        }
        choice = simpledialog.askstring("Select Area", "Choose area (Full Screen/Top-Left Quarter):")
        if choice in area_options:
            area = area_options[choice]
            if area:
                recording.set_recording_area(area)
                self.update_log(f"Recording area set to {area}")
            else:
                self.update_log("Custom area selection is not implemented.")
        else:
            self.update_log("Invalid area choice.")

# Run the application
if __name__ == "__main__":
    app = MousePad()
    app.mainloop()
