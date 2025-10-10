from TTS.api import TTS
import os
import threading

# Global TTS instance for better performance
_tts_instance = None
_tts_lock = threading.Lock()

def get_tts_instance():
    """Get or create TTS instance with thread safety"""
    global _tts_instance
    if _tts_instance is None:
        with _tts_lock:
            if _tts_instance is None:
                print("🤖 Initializing TTS model...")
                model_name = "tts_models/multilingual/multi-dataset/your_tts"
                _tts_instance = TTS(model_name=model_name, progress_bar=False, gpu=False)
                print("✅ TTS model loaded successfully")
    return _tts_instance

def generate_optimus_voice_yourtts(text, speaker_wav_path, output_path):
    """Generate speech using shared TTS instance"""
    try:
        print("🗣️ Generating speech...")
        tts = get_tts_instance()  # Use shared TTS instance
        
        tts.tts_to_file(
            text=text,
            speaker_wav=speaker_wav_path,
            language="en",
            file_path=output_path
        )
        
        print(f"✅ YourTTS success! Output: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ YourTTS failed: {e}")
        return False

def generate_speech_clean(text, output_path, speaker_wav):
    """Clean TTS generation function - same as original text_to_speech.py"""
    try:
        tts = get_tts_instance()
        
        # Use original text directly - no preprocessing overhead
        # This is exactly the same as the working text_to_speech.py
        tts.tts_to_file(
            text=text,
            speaker_wav=speaker_wav,
            language="en",
            file_path=output_path
        )
        
        return True
        
    except Exception as e:
        print(f"❌ Clean TTS generation failed: {e}")
        return False

def main():
    text = "I didn't understand the command sir. Please try again."
    speaker_wav = "optimus-clear_nZx1aJFy.wav"
    output_file = "optimus_prime_voice.wav"
    
    # Check if audio file exists
    if not os.path.exists(speaker_wav):
        print(f"❌ Audio file '{speaker_wav}' not found!")
        print("Please make sure you have the Optimus Prime audio sample in the same directory.")
        return
    
    print("🎬 Starting Optimus Prime voice cloning...")
    print(f"📝 Text: {text}")
    print(f"🎵 Reference audio: {speaker_wav}")

    if generate_optimus_voice_yourtts(text, speaker_wav, f"yourtts_{output_file}"):
            print("🎉 Successfully generated with YourTTS!")

if __name__ == "__main__":
    main()