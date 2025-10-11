import speech_recognition as sr
import pyaudio
import time
import threading

# Global variable to control microphone state
microphone_active = threading.Event()
microphone_active.set()  # Start with microphone active


# Global recognizer instance for better performance
_recognizer = None
_pyaudio = None

# Audio parameters
RATE = 16000
CHUNK = 1024
CHANNELS = 1
FORMAT = pyaudio.paInt16

def get_recognizer():
    """Get or create recognizer instance for better performance"""
    global _recognizer, _pyaudio
    if _recognizer is None:
        _recognizer = sr.Recognizer()
        _recognizer.dynamic_energy_threshold = True
        _recognizer.energy_threshold = 2500
        _recognizer.pause_threshold = 0.5
        _recognizer.operation_timeout = 2
        _recognizer.phrase_threshold = 0.3

        _pyaudio = pyaudio.PyAudio()
    return _recognizer, _pyaudio

def listen_for_command():
    """
    Optimized voice command listener with raw PyAudio input
    """
    if not microphone_active.is_set():
        time.sleep(0.05)
        return None

    recognizer, pa = get_recognizer()

    try:
        # Open raw audio stream
        stream = pa.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        print("🎙️ Listening (raw audio)...")

        # Capture audio for up to 3 seconds but check microphone state periodically
        frames = []
        for _ in range(int(RATE / CHUNK * 3)):  # 3 seconds worth of chunks
            if not microphone_active.is_set():  # Check if microphone was deactivated during capture
                stream.stop_stream()
                stream.close()
                return None
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

        stream.stop_stream()
        stream.close()

        # Convert raw frames into AudioData for recognizer
        audio_data = sr.AudioData(b"".join(frames), RATE, 2)

        # Recognize speech using Google
        text = recognizer.recognize_google(
            audio_data,
            language="en-US",
            show_all=False
        )

        print(f"✅ Recognized: {text}")
        return text.lower()

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
