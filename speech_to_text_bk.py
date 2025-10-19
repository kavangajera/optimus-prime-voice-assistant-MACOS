import speech_recognition as sr
import time
import threading

# Global variable to control microphone state
microphone_active = threading.Event()
microphone_active.set()  # Start with microphone active

# Global recognizer instance for better performance
_recognizer = None
_microphone = None

def get_recognizer():
    """Get or create recognizer and microphone instances for better performance"""
    global _recognizer, _microphone
    if _recognizer is None:
        _recognizer = sr.Recognizer()
        _recognizer.dynamic_energy_threshold = True
        _recognizer.energy_threshold = 2500
        _recognizer.pause_threshold = 2.0  # Stop listening after 2.0 seconds of silence
        _recognizer.operation_timeout = 2
        _recognizer.phrase_threshold = 0.3

        _microphone = sr.Microphone()
    return _recognizer, _microphone

def listen_for_command():
    """
    Voice command listener that listens continuously until silence is detected
    """
    if not microphone_active.is_set():
        time.sleep(0.05)
        return None

    recognizer, microphone = get_recognizer()

    try:
        print("🎙️ Listening...")

        # Listen continuously until pause_threshold (2.0s silence) is detected
        with microphone as source:
            audio = recognizer.listen(source, timeout=1, phrase_time_limit=10)

        # Recognize speech using Google
        text = recognizer.recognize_google(
            audio,
            language="en-US",
            show_all=False
        )

        print(f"✅ Recognized: {text}")
        return text.lower()

    except sr.WaitTimeoutError:
        # Timeout occurred, no speech detected within timeout period
        return None
    except sr.UnknownValueError:
        # Return None if no speech was recognized
        return None
    except sr.RequestError as e:
        print(f"❌ Speech recognition service error: {e}")
        return None
    except Exception as e:
        print(f"❌ Speech recognition error: {e}")
        return None

def main():
    """Test function for speech recognition"""
    print("🎙️ Speech Recognition Test (Raw Audio)")
    print("=" * 40)
    print("Say something (you have 3 seconds)...")

    command = listen_for_command()

    if command:
        print(f"📝 You said: {command}")
    else:
        print("🔇 No command recognized")

if __name__ == "__main__":
    main()