from TTS.api import TTS
import os

def generate_optimus_voice_yourtts(text, speaker_wav_path, output_path):
    """Fallback to YourTTS model"""
    try:
        print("🤖 Loading YourTTS model...")
        model_name = "tts_models/multilingual/multi-dataset/your_tts"
        tts = TTS(model_name=model_name, progress_bar=False, gpu=False)
        
        print("🗣️ Generating speech...")
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

def main():
    text = "I didn't understand that command sir. Please try again."
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