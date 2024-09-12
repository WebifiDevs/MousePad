from gui import MousePad
import tkinter as tk
from utils.shortcuts import register_shortcuts

# Main entry point for the application
if __name__ == "__main__":
    # Initialize the root Tkinter window
    root = tk.Tk()

    # Load the GUI components
    app = MousePad(root)

    # Register keyboard shortcuts
    register_shortcuts()

    # Start the Tkinter event loop
    root.mainloop()
