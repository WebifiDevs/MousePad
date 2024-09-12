import customtkinter as ctk
from recording import start_recording, stop_recording, save_actions, replay_actions, load_actions
from utils.shortcuts import register_shortcuts  # Import your register_shortcuts function here


class MousePad(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set up window
        self.title("MousePad")
        self.geometry("375x410")
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

        # Display the initial menu state
        self.show_menu_state()

        # Register keyboard shortcuts after the GUI is fully initialized
        self.register_shortcuts()

    def register_shortcuts(self):
        """Register keyboard shortcuts for the application."""
        register_shortcuts(self.update_gui_state, self.update_log)

    def clear_frame(self):
        """Clear the current frame for switching between states."""
        if self.current_frame is not None:
            self.current_frame.destroy()

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

        # Start and Play buttons
        self.record_button = ctk.CTkButton(self.current_frame, text="Start", font=("Nunito", 18), height=50, fg_color=self.button_color, command=self.toggle_recording)
        self.record_button.grid(row=2, column=0, pady=10, padx=20, sticky="ew")

        self.play_button = ctk.CTkButton(self.current_frame, text="Play", font=("Nunito", 18), height=50, fg_color=self.button_color, command=self.replay_recording)
        self.play_button.grid(row=3, column=0, pady=10, padx=20, sticky="ew")

        # View Shortcuts button
        shortcuts_button = ctk.CTkButton(self.current_frame, text="View Shortcuts", font=("Nunito", 18), height=50, fg_color=self.button_color)
        shortcuts_button.grid(row=4, column=0, pady=10, padx=20, sticky="ew")

    def toggle_recording(self):
        """Frame 3: Toggle between starting and stopping recording."""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        """Start recording and update the status."""
        self.is_recording = True
        self.update_log("Recording started...")
        self.record_button.configure(fg_color=self.recording_color, text="Stop")
        start_recording()

    def stop_recording(self):
        """Frame 4: Stop recording and display save options."""
        self.is_recording = False
        stop_recording()  # Stop the recording process
        self.update_log("Recording stopped.")
        self.record_button.configure(fg_color=self.button_color, text="Start")
        self.show_save_state()

    def replay_recording(self):
        """Replay the recorded actions."""
        self.update_log("Replaying recorded actions...")
        replay_actions(self.update_log)

    def update_log(self, message):
        """Update the log area with new messages."""
        if self.log_text:
            self.log_text.insert("end", f"{message}\n")
            self.log_text.yview_moveto(1)  # Scroll to the bottom

    def update_gui_state(self, is_recording):
        """Update the GUI state based on recording status."""
        self.is_recording = is_recording
        if is_recording:
            self.record_button.configure(fg_color=self.recording_color, text="Stop Recording")
        else:
            self.record_button.configure(fg_color=self.button_color, text="Start Recording")

    def show_save_state(self):
        """Frame 5: Show the modal for saving the recording."""
        self.clear_frame()
        self.current_frame = ctk.CTkFrame(self, fg_color='#262E3F')
        self.current_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Title
        title_label = ctk.CTkLabel(self.current_frame, text="Save Recording", font=("Nunito", 24, "bold"), text_color="white")
        title_label.grid(row=0, column=0, pady=10, sticky="ew")

        # File Name Entry
        file_label = ctk.CTkLabel(self.current_frame, text="File name:", font=("Nunito", 18), text_color="white")
        file_label.grid(row=1, column=0, pady=5, sticky="ew")

        file_entry = ctk.CTkEntry(self.current_frame, font=("Nunito", 18), fg_color='#262E3F', text_color="white")
        file_entry.grid(row=2, column=0, pady=5, sticky="ew")

        # Save and Cancel buttons
        button_frame = ctk.CTkFrame(self.current_frame, fg_color='#262E3F')
        button_frame.grid(row=3, column=0, pady=20, sticky="ew")

        cancel_button = ctk.CTkButton(button_frame, text="Cancel", font=("Nunito", 18), height=50, fg_color="red", command=self.show_menu_state)
        cancel_button.grid(row=0, column=0, padx=10)

        save_button = ctk.CTkButton(button_frame, text="Save", font=("Nunito", 18), height=50, fg_color="green", command=lambda: self.save_recording(file_entry.get()))
        save_button.grid(row=0, column=1, padx=10)

    def save_recording(self, filename):
        """Save the recorded actions."""
        save_actions(filename)
        self.update_log(f"Recording saved as {filename}")
        self.show_menu_state()

    def show_load_state(self):
        """Placeholder for load state."""
        load_actions()
        self.update_log("Loaded recording.")

    def show_how_state(self):
        """Placeholder for how it works state."""
        self.update_log("Displaying how-to information...")

# Run the application
if __name__ == "__main__":
    app = MousePad()
    app.mainloop()
