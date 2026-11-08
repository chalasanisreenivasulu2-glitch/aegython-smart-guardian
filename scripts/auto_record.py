"""
scripts/auto_record.py
Fully automated screen recorder for the AEGYTHON demo video.
"""
import cv2
import numpy as np
import pyautogui
import time
import threading
import sys

# --- Configuration ---
OUTPUT_FILE = "aegython_demo_automated.mp4"
FPS = 10.0
RECORDING = True

def record_screen():
    """Background thread to capture the screen."""
    global RECORDING
    
    # Get screen resolution
    screen_size = pyautogui.size()
    # Ensure it's even (required by some codecs)
    width, height = (screen_size.width // 2) * 2, (screen_size.height // 2) * 2
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(OUTPUT_FILE, fourcc, FPS, (width, height))
    
    print(f"[*] Recording started in background. Resolution: {width}x{height}")
    
    while RECORDING:
        # Capture screen
        img = pyautogui.screenshot()
        # Convert to numpy array and then BGR (which OpenCV uses)
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Resize if necessary
        frame = cv2.resize(frame, (width, height))
        
        out.write(frame)
        time.sleep(1.0 / FPS) # Limit frame rate to save CPU and disk space

    out.release()
    print(f"[*] Video saved as: {OUTPUT_FILE}")


def type_command(cmd):
    """Types a command slowly so it looks human."""
    for char in cmd:
        pyautogui.write(char)
        time.sleep(0.02)
    pyautogui.press('enter')

if __name__ == "__main__":
    print("==================================================")
    print("🚀 STARTING AUTOMATED DEMO RECORDING IN 5 SECONDS")
    print("==================================================")
    print("Please make sure this terminal is focused and maximized.")
    
    time.sleep(5) # Give you 5 seconds to focus the terminal
    
    # Start the recording thread
    recorder_thread = threading.Thread(target=record_screen)
    recorder_thread.start()
    
    time.sleep(2) # Wait 2 seconds before typing
    
    # Step 1: Run the tests
    print("\n[Automation] Running tests...")
    type_command("pytest -v")
    time.sleep(8) # Wait for pytest to finish (it takes ~2-3 seconds)
    
    # Step 2: Clear screen
    print("\n[Automation] Clearing screen...")
    type_command("cls")
    time.sleep(1)
    
    # Step 3: Run the demo script
    print("\n[Automation] Running the Smart Login Guardian demo...")
    type_command("python scripts/record_demo.py")
    
    # Wait for the demo script to finish (it has 2-second pauses between scenarios)
    # The script takes roughly 15-20 seconds to complete.
    time.sleep(25) 
    
    # Step 4: Stop recording
    print("\n[Automation] Stopping recording...")
    RECORDING = False
    recorder_thread.join()
    
    print("\n✅ Automation complete. Check the folder for the MP4 file.")