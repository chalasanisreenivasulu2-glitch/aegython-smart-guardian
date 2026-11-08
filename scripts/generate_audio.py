from gtts import gTTS
import os

os.makedirs("demo_assets", exist_ok=True)

scripts = {
    "01_intro.mp3": "Hello, I am Ch Sreenivasulu. This is Smart Login Guardian for AEGYTHON 2026. It detects and explains anomalous logins.",
    "02_tests.mp3": "First, here is the test evidence. The machine learning model and API endpoints pass all 8 tests.",
    "03_normal.mp3": "Now we run the demo. Here is a normal login. The model calculates a low risk score and correctly suggests to allow.",
    "04_attack.mp3": "Here is an impossible travel attack. The model flags it, suggests MFA, and clearly explains that the geo velocity was the primary risk factor.",
    "05_weekend.mp3": "Finally, an off hours login. The explanation highlights the new device and weekend flags.",
    "06_outro.mp3": "The full setup, architecture, and interactive UI are available in the GitHub repository. Thank you."
}

for filename, text in scripts.items():
    print(f"Generating {filename}...")
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(f"demo_assets/{filename}")

print("Audio generation complete.")