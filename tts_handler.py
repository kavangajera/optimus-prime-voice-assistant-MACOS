"""
Text-to-speech module for the Optimus Prime Voice Assistant
"""
import time
import os
from text_to_speech import get_tts_instance, generate_speech_clean


class TTSHandler:
    def __init__(self, audio_handler):
        self.audio_handler = audio_handler

    def speak_text_clean(self, text, electron_controller=None):
        """
        Direct TTS function - exactly like text_to_speech.py
        No layers, no extra processing, direct TTS call
        """
        try:
            # Play animation when speaking starts
            if electron_controller:
                electron_controller.play_animation()
            
            # Check if reference audio exists
            speaker_wav = "optimus-clear_nZx1aJFy.wav"
            output_path = "response.wav"
            
            if not os.path.exists(speaker_wav):
                print(f"❌ Audio file '{speaker_wav}' not found!")
                if electron_controller:
                    electron_controller.pause_animation()
                return False
            
            print(f"🗣️ Speaking: {text}")
            
            # DIRECT TTS CALL - exactly like text_to_speech.py
            tts = get_tts_instance()
            tts.tts_to_file(
                text=text,
                speaker_wav=speaker_wav,
                language="en",
                file_path=output_path
            )
            
            # Additional wait for file to be completely written by the TTS process
            # The TTS process may still be writing even after the function returns
            time.sleep(0.5)  # Wait for TTS process to finish writing
            
            # Direct audio playback - no extra layers
            self.audio_handler.play_audio_file(output_path, speed=1.0, quality=1)
            
            time.sleep(0.5)  # Brief pause to ensure audio finishes
            # Pause animation when speaking ends
            if electron_controller:
                import threading
                threading.Timer(0.2, electron_controller.pause_animation).start()
                
            return True
            
        except Exception as e:
            print(f"❌ Direct TTS failed: {e}")
            if electron_controller:
                electron_controller.pause_animation()
            return False

    def generate_speech_async(self, text, output_path, speaker_wav):
        """Generate speech using the clean method from text_to_speech.py"""
        try:
            print(f"🗣️ Generating speech for: {text[:50]}...")
            
            # Use the clean TTS generation from text_to_speech.py
            success = generate_speech_clean(text, output_path, speaker_wav)
            
            if success:
                print(f"✅ Speech generated successfully: {output_path}")
                return True
            else:
                print(f"❌ Speech generation failed")
                return False
                
        except Exception as e:
            print(f"❌ Speech generation failed: {e}")
            return False

    def speak_text(self, text, electron_controller=None):
        """
        Clean and fast text-to-speech like text_to_speech.py
        """
        try:
            # Play animation when speaking starts
            if electron_controller:
                electron_controller.play_animation()
            
            # Check if reference audio exists
            speaker_wav = "optimus-clear_nZx1aJFy.wav"
            output_path = "response.wav"
            
            if not os.path.exists(speaker_wav):
                print(f"❌ Audio file '{speaker_wav}' not found!")
                if electron_controller:
                    electron_controller.pause_animation()
                return False
            
            # Set audio playing flag to indicate TTS is happening
            self.audio_handler.is_audio_playing.set()
            
            try:
                # Generate speech directly - no thread pool overhead
                if self.generate_speech_async(text, output_path, speaker_wav):
                    # Additional wait for file to be completely written by the TTS process
                    time.sleep(0.5)  # Wait for TTS process to finish writing
                    
                    # Play audio directly - no thread pool
                    self.audio_handler.play_audio_file(output_path, speed=1.0, quality=1)
                else:
                    print("❌ Speech generation failed")
                    return False
                        
            finally:
                # Always clear the audio playing flag after playback
                self.audio_handler.is_audio_playing.clear()
            
            # Pause animation when speaking ends
            if electron_controller:
                import threading
                threading.Timer(0.2, electron_controller.pause_animation).start()
                
            return True
            
        except Exception as e:
            print(f"❌ Text-to-speech failed: {e}")
            self.audio_handler.is_audio_playing.clear()
            if electron_controller:
                electron_controller.pause_animation()
            return False