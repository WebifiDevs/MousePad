 MousePAd

## Overview

This tool allows you to record mouse movements and clicks, replay them, and save/load recorded actions. It supports global keyboard shortcuts for easy control.

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application: 
   ```bash 
   python main.py
   ```

## Keyboard Shortcuts

| Shortcut | Description |
|----------|-------------|
| Ctrl+R   | Start recording mouse actions |
| Ctrl+S   | Stop recording mouse actions |
| Ctrl+P   | Replay recorded actions |
| Ctrl+Q   | Save recorded actions to file |
| Ctrl+L   | Load recorded actions from file |

## Configuration

Modify the keyboard shortcuts and other settings by editing the config.json file.

## Saving and Loading Actions

Recorded actions are saved as JSON files in the actions/ folder. You can load a previously recorded sequence and replay it.

