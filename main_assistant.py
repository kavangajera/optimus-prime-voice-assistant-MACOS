import speech_recognition as sr
import time
import os
import sys
import re
import subprocess
import threading

# Import our custom modules
from app_launcher import open_app, close_app, play_music, send_whatsapp_message
from speech_to_text import listen_for_command, stop_microphone, start_microphone
# Import text to speech functions
from TTS.api import TTS
# Import Electron controller
from electron_controller import ElectronController

# Global variable to track audio state
is_audio_playing = threading.Event()

def speak_text(text, electron_controller=None):
    """
    Convert text to speech using the Optimus Prime voice
    """
    try:
        # Play animation when speaking starts
        if electron_controller:
            electron_controller.play_animation()
        
        # Initialize TTS with YourTTS model (reuse instance for better performance)
        if not hasattr(speak_text, 'tts'):
            model_name = "tts_models/multilingual/multi-dataset/your_tts"
            speak_text.tts = TTS(model_name=model_name, progress_bar=False, gpu=False)
        
        # Generate speech with Optimus Prime voice
        speaker_wav = "optimus-clear_nZx1aJFy.wav"
        output_path = "response.wav"
        
        # Check if reference audio exists
        if not os.path.exists(speaker_wav):
            print(f"❌ Audio file '{speaker_wav}' not found!")
            # Pause animation if speech generation fails
            if electron_controller:
                electron_controller.pause_animation()
            return False
            
        # Preprocess text to handle common issues that cause word skipping
        # Replace common abbreviations and problematic punctuation
        processed_text = text.replace("...", " dot dot dot ")
        processed_text = processed_text.replace("Mr.", "Mister ")
        processed_text = processed_text.replace("Mrs.", "Missus ")
        processed_text = processed_text.replace("Dr.", "Doctor ")
        processed_text = processed_text.replace("Prof.", "Professor ")
        processed_text = processed_text.replace("St.", "Saint ")
        processed_text = processed_text.replace("Ave.", "Avenue ")
        processed_text = processed_text.replace("Rd.", "Road ")
        processed_text = processed_text.replace("Ln.", "Lane ")
        processed_text = processed_text.replace("etc.", "et cetera ")
        processed_text = processed_text.replace("vs.", "versus ")
        processed_text = processed_text.replace("i.e.", "that is ")
        processed_text = processed_text.replace("e.g.", "for example ")
        processed_text = processed_text.replace("cf.", "compare ")
        processed_text = processed_text.replace("al.", "and others ")
        
        # Remove extra whitespace and ensure clean text
        import re
        processed_text = re.sub(r'\s+', ' ', processed_text).strip()
        
        # Generate the speech
        speak_text.tts.tts_to_file(
            text=processed_text,
            speaker_wav=speaker_wav,
            language="en",
            file_path=output_path
        )
        
        # Wait briefly to ensure file is written before playing
        time.sleep(0.1)
        
        # Set audio playing flag to temporarily stop microphone
        is_audio_playing.set()
        # Stop microphone explicitly to prevent conflicts
        stop_microphone()
        
        try:
            # Play the generated audio (using subprocess for non-blocking playback)
            # Using a simple afplay command to reduce audio conflicts
            subprocess.call(["afplay", output_path])
        finally:
            # Always clear the audio playing flag after playback
            is_audio_playing.clear()
            # Resume microphone after a brief delay to avoid conflicts
            threading.Timer(0.5, start_microphone).start()
        
        # Pause animation when speaking ends (after a short delay to allow playback to start)
        if electron_controller:
            threading.Timer(0.5, electron_controller.pause_animation).start()
            
        return True
        
    except Exception as e:
        print(f"❌ Text-to-speech failed: {e}")
        # Pause animation if speech generation fails
        if electron_controller:
            electron_controller.pause_animation()
        # Clear the audio playing flag in case of error
        is_audio_playing.clear()
        # Ensure microphone is started again even if there's an error
        start_microphone()
        return False

def extract_music_command(command):
    """
    Extract music command from voice command
    """
    # Common patterns for playing music
    music_patterns = [
        r"play\s+(?:the\s+)?(?:song\s+)?(.+)",
        r"play\s+(?:the\s+)?(?:music\s+)?(.+)",
        r"listen\s+to\s+(?:the\s+)?(.+)",
        r"put\s+on\s+(?:the\s+)?(.+)"
    ]
    
    # Check for music commands
    for pattern in music_patterns:
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            song_name = match.group(1).strip()
            # Remove "for me" or "for me sir" if present
            song_name = re.sub(r"\s+for\s+me.*$", "", song_name)
            return song_name
    
    return None

def extract_app_name(command):
    """
    Extract application name from voice command
    """
    # Common patterns for opening apps
    open_patterns = [
        r"open\s+(.+)",
        r"launch\s+(.+)",
        r"start\s+(.+)",
        r"open\s+app\s+(.+)",
        r"please\s+open\s+(.+)"
    ]
    
    # Common patterns for closing apps
    close_patterns = [
        r"close\s+(.+)",
        r"quit\s+(.+)",
        r"exit\s+(.+)",
        r"shut\s+down\s+(.+)",
        r"please\s+close\s+(.+)"
    ]
    
    # Check for open commands
    for pattern in open_patterns:
        match = re.search(pattern, command)
        if match:
            app_name = match.group(1).strip()
            # Remove "for me" or "for me sir" if present
            app_name = re.sub(r"\s+for\s+me.*$", "", app_name)
            return ("open", app_name)
    
    # Check for close commands
    for pattern in close_patterns:
        match = re.search(pattern, command)
        if match:
            app_name = match.group(1).strip()
            # Remove "for me" or "for me sir" if present
            app_name = re.sub(r"\s+for\s+me.*$", "", app_name)
            return ("close", app_name)
    
    return None

def process_command(command, electron_controller=None):
    """
    Process the recognized voice command
    """
    if not command:
        # Pause animation when no command is received
        if electron_controller:
            electron_controller.pause_animation()
        return True  # Continue listening
    
    # Check for exit command
    if "transform optimus" in command.lower():
        response = "Rollouting Sir! Good bye..."
        print(f"🤖 {response}")
        speak_text(response, electron_controller)
        return False  # Stop listening
    
    # Check for music commands
    song_name = extract_music_command(command)
    if song_name:
        response = f"Playing {song_name} for you sir!"
        print(f"🤖 {response}")
        speak_text(response, electron_controller)
        # Set audio playing flag to temporarily stop microphone during music playback
        is_audio_playing.set()
        # Stop microphone explicitly to prevent conflicts
        stop_microphone()
        try:
            play_music(song_name)
        finally:
            # Wait a bit before resuming microphone to avoid immediate conflicts
            threading.Timer(2.0, lambda: _resume_microphone()).start()
        return True
    
    # Check for WhatsApp message commands
    # Looking for patterns like "message contact with message" or "send message to contact with message"
    whatsapp_match = re.search(r"(?:message|send.*?message.*?to|whatsapp)\s+(.+?)\s+(?:with|saying)\s+(.+)", command, re.IGNORECASE)
    if whatsapp_match:
        contact_name = whatsapp_match.group(1).strip()
        message = whatsapp_match.group(2).strip()
        # Remove "for me" or "for me sir" if present
        contact_name = re.sub(r"\s+for\s+me.*$", "", contact_name)
        message = re.sub(r"\s+for\s+me.*$", "", message)
        
        response = f"Sending message to {contact_name} for you sir!"
        print(f"🤖 {response}")
        speak_text(response, electron_controller)
        send_whatsapp_message(contact_name, message)
        return True
    
    # Extract app name and action from command
    action_info = extract_app_name(command)
    
    if action_info:
        action, app_name = action_info
        
        if action == "open":
            response = f"Opening {app_name} for you sir!"
            print(f"🤖 {response}")
            speak_text(response, electron_controller)
            open_app(app_name)
        elif action == "close":
            response = f"Closing {app_name} for you sir!"
            print(f"🤖 {response}")
            speak_text(response, electron_controller)
            close_app(app_name)
    else:
        response = "I didn't understand that command sir. Please try again."
        print(f"🤖 {response}")
        speak_text(response, electron_controller)
    
    return True  # Continue listening

def _resume_microphone():
    """Internal function to resume microphone after a delay"""
    is_audio_playing.clear()
    start_microphone()

def main():
    """
    Main voice assistant loop
    """
    # Initialize Electron controller
    electron_controller = ElectronController()
    
    # Start Electron app    
    if not electron_controller.start_electron_app():
        print("❌ Failed to start 3D animation. Continuing without it.")
    
    print("🤖 Optimus Prime Voice Assistant")
    print("=" * 40)
    print("🎙️ Say 'Transform and Rollout' to exit the assistant")
    print("🗣️ Example commands:")
    print("   - 'Open WhatsApp for me'")
    print("   - 'Close Safari'")
    print("   - 'Launch Visual Studio Code'")
    print("   - 'Play Bohemian Rhapsody'")
    print("   - 'Listen to some jazz'")
    print("   - 'Message John with Hello there'")
    print("   - 'Send a message to Jane saying How are you?'")
    print("   - 'Transform and Rollout'")
    print("=" * 40)
    
    # Welcome message (make it shorter for quicker startup)
    welcome_msg = "Hello sir, I am Optimus Prime. How can I assist you?"
    print(f"🤖 {welcome_msg}")
    speak_text(welcome_msg, electron_controller)
    
    # Track time since last user interaction
    last_interaction_time = time.time()
    inactivity_timeout = 2  # Reduced timeout for quicker animation pause
    
    # Main listening loop
    while True:
        # Add a small delay to reduce CPU usage and potentially reduce audio conflicts
        time.sleep(0.1)
        
        # Skip listening if audio is currently playing to avoid conflicts
        if is_audio_playing.is_set():
            # Still process any pending commands but don't listen for new ones
            if not process_command(None, electron_controller):
                break
            continue
        
        command = listen_for_command()
        
        # Check for inactivity timeout
        current_time = time.time()
        if current_time - last_interaction_time > inactivity_timeout:
            # Pause animation due to inactivity
            if electron_controller:
                electron_controller.pause_animation()
        
        if not process_command(command, electron_controller):
            break
            
        # Update last interaction time if a command was received
        if command is not None:
            last_interaction_time = time.time()

if __name__ == "__main__":
    main()