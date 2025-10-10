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

# Global recognizer instance for better performance
_recognizer = None
_microphone = None

def get_recognizer():
    """Get or create recognizer instance for better performance"""
    global _recognizer, _microphone
    if _recognizer is None:
        _recognizer = sr.Recognizer()
        _recognizer.dynamic_energy_threshold = True
        _recognizer.energy_threshold = 2500  # Lower threshold for better music compatibility
        _recognizer.pause_threshold = 0.5  # Faster response
        _recognizer.operation_timeout = 2  # Shorter timeout for better performance
        _recognizer.phrase_threshold = 0.3  # Lower phrase threshold for music environments
        
        # Create microphone instance once
        _microphone = sr.Microphone()
        # Adjust for ambient noise once at startup
        with _microphone as source:
            _recognizer.adjust_for_ambient_noise(source, duration=0.1)
    
    return _recognizer, _microphone

def listen_for_command():
    """
    Optimized voice command listener with better performance and music compatibility
    """
    # Check if microphone is currently active
    if not microphone_active.is_set():
        time.sleep(0.05)  # Reduced pause for better responsiveness
        return None
    
    recognizer, microphone = get_recognizer()
    
    try:
        # Listen for audio with optimized settings for music environments
        with microphone as source:
            # Quick ambient noise adjustment - shorter for music compatibility
            recognizer.adjust_for_ambient_noise(source, duration=0.05)
            
            # Listen with optimized settings for music environments
            audio = recognizer.listen(
                source, 
                timeout=2,  # Shorter timeout for better responsiveness
                phrase_time_limit=3  # Shorter phrase limit for music environments
            )
            
            # Recognize speech using Google Speech Recognition with music-friendly settings
            text = recognizer.recognize_google(
                audio, 
                language="en-US",
                show_all=False  # Don't show all alternatives for better performance
            )
            
            print(f"✅ Recognized: {text}")
            return text.lower()
            
    except sr.WaitTimeoutError:
        # Don't print timeout messages to reduce noise
        return None
    except sr.UnknownValueError:
        # Don't print unknown value errors to reduce noise
        return None
    except sr.RequestError as e:
        print(f"❌ Speech recognition service error: {e}")
        return None
    except Exception as e:
        print(f"❌ Speech recognition error: {e}")
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