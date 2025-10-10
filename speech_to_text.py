import speech_recognition as sr
import time
import threading

# Global variable to control microphone state
microphone_active = threading.Event()
microphone_active.set()  # Start with microphone active

def stop_microphone():
    """Stops the microphone to avoid conflicts with audio playback"""
    global microphone_active
    microphone_active.clear()
    print("🔴 Microphone stopped (to prevent audio conflicts)")

def start_microphone():
    """Starts the microphone after audio playback is finished"""
    global microphone_active
    microphone_active.set()
    print("🟢 Microphone started")

def listen_for_command():
    """
    Listens for a voice command and returns the recognized text.
    Returns None if no speech is detected or an error occurs.
    """
    # Check if microphone is currently active
    if not microphone_active.is_set():
        time.sleep(0.1)  # Brief pause to allow other operations to complete
        return None
    
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 4000  # Adjust based on environment
    recognizer.pause_threshold = 0.8  # Seconds of non-speaking audio before a phrase is considered complete
    
    # Create microphone instance with specific parameters to reduce conflicts
    with sr.Microphone() as source:
        print("🎙️ Listening for command...")
        # Minimal ambient noise adjustment for faster startup
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        
        try:
            # Listen for audio with no timeout to wait indefinitely for speech
            # Using phrase_time_limit to control maximum phrase length
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            print("🔄 Processing audio...")
            
            # Recognize speech using Google Speech Recognition
            text = recognizer.recognize_google(audio)
            print(f"✅ Recognized: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("⏰ No speech detected within timeout period")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Could not request results from Google Speech Recognition service; {e}")
            return None
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            return None

def main():
    """Test function for speech recognition"""
    print("🎙️ Speech Recognition Test")
    print("=" * 30)
    print("Say something (you have 10 seconds)...")
    
    command = listen_for_command()
    
    if command:
        print(f"📝 You said: {command}")
    else:
        print("🔇 No command recognized")

if __name__ == "__main__":
    main()