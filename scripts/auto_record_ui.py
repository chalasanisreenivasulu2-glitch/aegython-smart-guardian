import cv2
import numpy as np
import pyautogui
import time
import threading
import os
import subprocess
import webbrowser
import pygetwindow as gw
from playsound import playsound
from moviepy import VideoFileClip, AudioFileClip, concatenate_audioclips

OUTPUT_VIDEO = "aegython_demo_2min.mp4"
TEMP_VIDEO = "temp_video.mp4"
FPS = 10.0
RECORDING = True

def record_screen():
    global RECORDING
    screen_size = pyautogui.size()
    width, height = (screen_size.width // 2) * 2, (screen_size.height // 2) * 2
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(TEMP_VIDEO, fourcc, FPS, (width, height))
    while RECORDING:
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (width, height))
        out.write(frame)
        time.sleep(1.0 / FPS)
    out.release()

def play_and_wait(filename):
    print(f"Playing: {filename}")
    playsound(f"demo_assets/{filename}", block=True) 

if __name__ == "__main__":
    # 1. Start Streamlit
    streamlit_process = subprocess.Popen(
        [".\\venv\\Scripts\\streamlit.exe", "run", "frontend/dashboard.py", "--server.headless=true"], 
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    print("Waiting 12s for Streamlit...")
    time.sleep(12)
    
    # 2. Open Chrome
    print("Launching Browser...")
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if os.path.exists(chrome_path):
        subprocess.Popen([chrome_path, "--start-maximized", "http://localhost:8501"])
    else:
        webbrowser.open("http://localhost:8501")
    
    print("Waiting 10s for UI to load...")
    time.sleep(10)
    
    # 3. FORCE MAXIMIZE
    print("Forcing window maximize...")
    try:
        windows = gw.getWindowsWithTitle('Streamlit') + gw.getWindowsWithTitle('localhost')
        if windows:
            win = windows[0]
            win.maximize()
            win.activate()
    except Exception:
        pyautogui.hotkey('win', 'up')
    
    time.sleep(3)

    # 4. Start Recording
    print("Starting recording in 3 seconds...")
    time.sleep(3)
    recorder_thread = threading.Thread(target=record_screen)
    recorder_thread.start()
    
    # --- TIMED SEQUENCE WITH KEYBOARD NAVIGATION ---
    
    play_and_wait("01_intro.mp3")
    time.sleep(2)
    
    # 2. Normal Login (Use Keyboard to avoid coordinate misses)
    play_and_wait("03_normal.mp3")
    
    # First, click anywhere in the center of the screen just to focus the browser window
    pyautogui.click(pyautogui.size().width // 2, pyautogui.size().height // 2)
    time.sleep(1)
    
    # Use Tab to navigate. The very first Tab highlights the Normal button.
    pyautogui.press('tab')
    time.sleep(0.5)
    pyautogui.press('enter') # Click Normal
    time.sleep(2)
    
    # Navigate down to the Analyze button. 
    # Depending on Streamlit, it might take 5-7 tabs to reach the Analyze button.
    # We will press tab 6 times.
    for _ in range(6):
        pyautogui.press('tab')
        time.sleep(0.2)
    pyautogui.press('enter') # Click Analyze
    time.sleep(8) 
    
    # 3. Attack Login
    play_and_wait("04_attack.mp3")
    # To reset the view, we tab back up to the buttons.
    # Shift+Tab goes backwards.
    for _ in range(7):
        pyautogui.hotkey('shift', 'tab')
        time.sleep(0.2)
        
    pyautogui.press('tab') # Move to Attack button
    pyautogui.press('enter')
    time.sleep(2)
    
    for _ in range(6):
        pyautogui.press('tab')
        time.sleep(0.2)
    pyautogui.press('enter') # Click Analyze
    time.sleep(10)
    
    # 4. Weekend
    play_and_wait("05_weekend.mp3")
    for _ in range(7):
        pyautogui.hotkey('shift', 'tab')
        time.sleep(0.2)
        
    pyautogui.press('tab') # Move to Weekend button
    pyautogui.press('tab') # Move to Weekend button
    pyautogui.press('enter')
    time.sleep(2)
    
    for _ in range(6):
        pyautogui.press('tab')
        time.sleep(0.2)
    pyautogui.press('enter') # Click Analyze
    time.sleep(10)
    
    play_and_wait("06_outro.mp3")
    time.sleep(5)
    
    print("Stopping recording...")
    RECORDING = False
    recorder_thread.join()
    streamlit_process.terminate()
    
    # --- COMBINE AUDIO AND VIDEO ---
    print("Stitching video and audio...")
    audio_clips = []
    for f in ["01_intro.mp3", "03_normal.mp3", "04_attack.mp3", "05_weekend.mp3", "06_outro.mp3"]:
        audio_clips.append(AudioFileClip(f"demo_assets/{f}"))
    
    final_audio = concatenate_audioclips(audio_clips)
    final_audio.write_audiofile("temp_audio.mp3", logger=None)
    
    video = VideoFileClip(TEMP_VIDEO)
    audio = AudioFileClip("temp_audio.mp3")
    
    final_video = video.with_audio(audio).subclipped(0, audio.duration)
    final_video.write_videofile(OUTPUT_VIDEO, codec="libx264", audio_codec="aac", fps=FPS, logger=None)
    
    print(f"✅ Done! Video saved to {OUTPUT_VIDEO}")