import time
import os
import re
import subprocess
import threading
import queue
import psutil

# Import our custom modules
from app_launcher import open_app, close_app, play_music, send_whatsapp_message, monitor_music_playback
from speech_to_text import listen_for_command, microphone_active
# Import text to speech functions
from text_to_speech import get_tts_instance, generate_speech_clean
# Import Electron controller
from electron_controller import ElectronController

# Global variables for performance optimization
is_audio_playing = threading.Event()
is_music_playing = threading.Event()  # New event to track music playback
tts_queue = queue.Queue()
audio_queue = queue.Queue()
tts_executor = None
audio_executor = None


def wait_for_file_write_complete(file_path, timeout=15):
    """
    Wait for a file to be completely written by checking its size over time.
    This is crucial for preventing issues where audio is cut off because playback starts before writing is complete.
    Extended timeout and more thorough checks to ensure complete file writing.
    """
    import time
    import os
    start_time = time.time()
    
    # Wait until the file exists
    while not os.path.exists(file_path):
        if time.time() - start_time > timeout:
            return False
        time.sleep(0.05)
    
    # Monitor the file size to ensure writing is complete
    # Use multiple checks to ensure file is really done being written
    size_checks = []
    stable_count = 0
    required_stable_checks = 5  # Require 5 consistent readings
    
    while True:
        try:
            current_size = os.path.getsize(file_path)
            size_checks.append(current_size)
            
            # Keep last several size checks
            if len(size_checks) > required_stable_checks:
                size_checks = size_checks[-required_stable_checks:]
            
            # Check if all recent size readings are the same
            if len(size_checks) >= required_stable_checks and len(set(size_checks)) == 1:
                stable_count += 1
                if stable_count >= 2:  # Require stability for 2 consecutive checks
                    # Additional delay to ensure file handle is completely released
                    time.sleep(0.2)
                    return True
            else:
                stable_count = 0  # Reset if size changes
            
            time.sleep(0.1)
            
            if time.time() - start_time > timeout:
                # Timeout reached but file exists, return True to try to play it
                time.sleep(0.1)  # Small additional delay
                return True
        except OSError:
            time.sleep(0.05)
            continue


def play_audio_file(audio_path, speed=1.0, quality=1, volume=None):
    """
    Centralized function to play audio files using afplay with enhanced settings to prevent word skipping
    """
    import time
    
    # Check if the audio file exists and is completely written
    if not wait_for_file_write_complete(audio_path):
        print(f"❌ Audio file not ready for playback: {audio_path}")
        return False
    
    # Additional safety: try to open and briefly read the file to ensure it's accessible
    try:
        with open(audio_path, 'rb') as f:
            # Read first 100 bytes to ensure file is readable and not locked
            f.read(100)
        # Small delay to allow any file handles to be properly released
        time.sleep(0.2)
    except Exception as e:
        print(f"❌ Cannot access audio file: {e}")
        return False
    
    try:
        # Build afplay command with enhanced quality settings
        cmd = ["afplay"]
        
        # Add quality setting - higher value for better quality (1 is high quality)
        cmd.extend(["-q", str(quality)])
        
        # Add speed setting if different from normal (1.0 is normal)
        if speed != 1.0:
            cmd.extend(["-r", str(speed)])
        
        # Add volume setting if specified (0.0 to 1.0, where 1.0 is maximum)
        if volume is not None:
            cmd.extend(["-v", str(volume)])
        
        # Add the audio file path
        cmd.append(audio_path)
        
        # Use the afplay command with optimized settings
        # Using a generous timeout to ensure complete playback
        result = subprocess.run(cmd, check=True, timeout=90, capture_output=True)
        
        # Ensure the subprocess completes properly
        if result.returncode == 0:
            # Additional delay after playback to ensure complete processing
            time.sleep(0.3)
            return True
        else:
            print(f"❌ afplay returned non-zero: {result.returncode}")
            if result.stderr:
                print(f"   stderr: {result.stderr.decode()}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Audio playback timeout")
        return False
    except Exception as e:
        print(f"❌ Audio playback failed: {e}")
        if 'result' in locals() and hasattr(result, 'stderr') and result.stderr:
            stderr_output = result.stderr.decode().strip()
            if stderr_output:
                print(f"   afplay stderr: {stderr_output}")
        return False

# Removed preprocess_text_for_tts function - using direct TTS calls for better performance

def speak_text_clean(text, electron_controller=None):
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
        play_audio_file(output_path, speed=1.0, quality=1)
        
        time.sleep(0.5)  # Brief pause to ensure audio finishes
        # Pause animation when speaking ends
        if electron_controller:
            threading.Timer(0.2, electron_controller.pause_animation).start()
            
        return True
        
    except Exception as e:
        print(f"❌ Direct TTS failed: {e}")
        if electron_controller:
            electron_controller.pause_animation()
        return False

def generate_speech_async(text, output_path, speaker_wav):
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

def play_audio_async(audio_path):
    """Play audio in a separate thread to avoid blocking"""
    return play_audio_file(audio_path, speed=1.0, quality=1)

def speak_text(text, electron_controller=None):
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
        is_audio_playing.set()
        
        try:
            # Generate speech directly - no thread pool overhead
            if generate_speech_async(text, output_path, speaker_wav):
                # Additional wait for file to be completely written by the TTS process
                time.sleep(0.5)  # Wait for TTS process to finish writing
                
                # Play audio directly - no thread pool
                play_audio_file(output_path, speed=1.0, quality=1)
            else:
                print("❌ Speech generation failed")
                return False
                    
        finally:
            # Always clear the audio playing flag after playback
            is_audio_playing.clear()
        
        # Pause animation when speaking ends
        if electron_controller:
            threading.Timer(0.2, electron_controller.pause_animation).start()
            
        return True
        
    except Exception as e:
        print(f"❌ Text-to-speech failed: {e}")
        is_audio_playing.clear()
        if electron_controller:
            electron_controller.pause_animation()
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
        speak_text_clean(response, electron_controller)
        return False  # Stop listening
    
    # Check for music commands
    song_name = extract_music_command(command)
    if song_name:
        response = f"Playing {song_name} for you sir!"
        print(f"🤖 {response}")
        
        # Start music playback with proper TTS and timing
        def play_music_with_tts():
            # Set the music playing flag to prevent microphone from starting/stopping
            is_music_playing.set()
            # Stop microphone completely during music playback
            microphone_active.clear()
            
            try:
                # Step 1: Play TTS response without microphone interference
                print(f"🗣️ Speaking: {response}")
                
                # Generate and play TTS without microphone management
                speaker_wav = "optimus-clear_nZx1aJFy.wav"
                output_path = "response.wav"
                
                if os.path.exists(speaker_wav):
                    # DIRECT TTS CALL - exactly like text_to_speech.py
                    tts = get_tts_instance()
                    tts.tts_to_file(
                        text=response,
                        speaker_wav=speaker_wav,
                        language="en",
                        file_path=output_path
                    )
                    
                    # Additional wait for file to be completely written by the TTS process
                    time.sleep(0.5)  # Wait for TTS process to finish writing
                    
                    # Direct audio playback
                    play_audio_file(output_path, speed=0.9, quality=1)
                
                # Step 2: Wait 1 second after TTS completes
                print("⏳ Waiting 1 second before starting music...")
                time.sleep(1.0)
                
                # Step 3: Start music playback and check if song exists
                print(f"🎵 Starting music playback for: {song_name}")
                music_success = play_music(song_name)
                
                if music_success:
                    print(f"🎵 Music playback initiated for: {song_name}")
                    print("⏳ Music is playing, microphone is off...")
                    # Monitor actual music playback to detect when it finishes
                    from app_launcher import monitor_music_playback
                    monitor_music_playback()
                else:
                    # Song not found - play error message
                    error_response = f"There is no song with name {song_name} in your Music library, sir"
                    print(f"🤖 {error_response}")
                    
                    # DIRECT TTS CALL for error message
                    if os.path.exists(speaker_wav):
                        tts = get_tts_instance()
                        tts.tts_to_file(
                            text=error_response,
                            speaker_wav=speaker_wav,
                            language="en",
                            file_path=output_path
                        )
                        
                        # Additional wait for file to be completely written by the TTS process
                        time.sleep(0.5)  # Wait for TTS process to finish writing
                        
                        # Direct audio playback
                        play_audio_file(output_path, speed=1.0, quality=1)
        
            except Exception as e:
                print(f"❌ Music playback error: {e}")
            finally:
                # Always clear the music playing flag when music playback is done
                is_music_playing.clear()
                # Resume microphone after music playback
                microphone_active.set()
             
        
        # Start music with TTS in independent thread
        # No microphone control during this process
        music_thread = threading.Thread(target=play_music_with_tts, daemon=True)
        music_thread.start()
        
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
        speak_text_clean(response, electron_controller)
        send_whatsapp_message(contact_name, message)
        return True
    
    # Extract app name and action from command
    action_info = extract_app_name(command)
    
    if action_info:
        action, app_name = action_info
        
        if action == "open":
            response = f"Opening {app_name} for you sir!"
            print(f"🤖 {response}")
            speak_text_clean(response, electron_controller)
            open_app(app_name)
        elif action == "close":
            response = f"Closing {app_name} for you sir!"
            print(f"🤖 {response}")
            speak_text_clean(response, electron_controller)
            close_app(app_name)
    else:
        response = "I didn't get the command sir. Please try to say it again."
        # print(f"🤖 {response}")
        speak_text_clean(response, electron_controller)
    
    return True  # Continue listening


def optimize_system_performance():
    """Optimize system performance for M3 Pro MacBook"""
    try:
        # Set process priority to high for better performance
        import os
        os.nice(-10)  # Higher priority
        
        # Optimize for M3 Pro architecture
        # Set environment variables for better performance
        os.environ['PYTHONUNBUFFERED'] = '1'
        os.environ['OMP_NUM_THREADS'] = '8'  # M3 Pro has 8 performance cores
        os.environ['MKL_NUM_THREADS'] = '8'
        
        # Configure psutil for better resource monitoring
        psutil.cpu_percent(interval=None)  # Initialize CPU monitoring
        
        print("🚀 System optimized for M3 Pro MacBook")
        print(f"💻 CPU Cores: {psutil.cpu_count()}")
        print(f"🧠 Memory: {psutil.virtual_memory().total // (1024**3)} GB")
        
    except Exception as e:
        print(f"⚠️ System optimization warning: {e}")

def monitor_system_resources():
    """Monitor system resources and adjust performance accordingly"""
    try:
        # Get current CPU and memory usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_percent = psutil.virtual_memory().percent
        
        # Adjust performance based on system load
        if cpu_percent > 80 or memory_percent > 85:
            print(f"⚠️ High system load - CPU: {cpu_percent}%, Memory: {memory_percent}%")
            return False  # Reduce processing
        elif cpu_percent > 60 or memory_percent > 70:
            print(f"📊 Moderate system load - CPU: {cpu_percent}%, Memory: {memory_percent}%")
            return True   # Normal processing
        else:
            return True   # Full performance
    except:
        return True  # Default to full performance if monitoring fails

def main():
    """
    Main voice assistant loop with optimized performance
    """
    # Optimize system performance first
    optimize_system_performance()
    
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
    speak_text_clean(welcome_msg, electron_controller)
    
    # Track time since last user interaction
    last_interaction_time = time.time()
    inactivity_timeout = 2  # Reduced timeout for quicker animation pause
    resource_check_counter = 0
    
    # Main listening loop with improved performance
    while True:
        # Monitor system resources periodically
        resource_check_counter += 1
        if resource_check_counter % 20 == 0:  # Check every 20 iterations
            system_ok = monitor_system_resources()
            if not system_ok:
                time.sleep(0.2)  # Longer delay if system is under load
            else:
                time.sleep(0.05)  # Normal delay
        else:
            time.sleep(0.05)
        
        # Handle listening based on current state (TTS vs music vs normal)
        if is_audio_playing.is_set():
            # During TTS playback, microphone is managed by the TTS functions
            # We still attempt to listen but with caution
            command = None
            try:
                # Try to listen with shorter timeout during TTS
                command = listen_for_command()
            except:
                pass
        elif is_music_playing.is_set():
            # During music playback, completely stop listening to prevent volume fluctuations
            # Music should play without any microphone interference
            command = None
            # Skip listening entirely during music playback
            # Check if user wants to stop music (this will be handled by system events)
            time.sleep(0.2)  # Longer pause to reduce CPU usage during music
        else:
            # Normal listening when neither TTS nor music is playing
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