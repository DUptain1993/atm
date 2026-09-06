import subprocess
import os

def speak(text, enabled=True):
    """Text to speech output"""
    if not enabled:
        return
    
    try:
        # Try espeak (common on Pi)
        subprocess.run(['espeak', text], capture_output=True, timeout=5)
    except:
        # Fallback to print
        print(f"[TTS] {text}")

def listen_placeholder():
    """
    Placeholder for speech input
    In production, this would use a library like speech_recognition
    """
    print("🎤 Listening (press Enter to stop)...")
    # For now, just return keyboard input
    return input("You: ")
