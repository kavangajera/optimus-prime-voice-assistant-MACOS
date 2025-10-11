"""
Audio handling module for the Optimus Prime Voice Assistant
"""
import time
import os
import subprocess
import threading


class AudioHandler:
    def __init__(self):
        self.is_audio_playing = threading.Event()
        self.is_music_playing = threading.Event()

    def wait_for_file_write_complete(self, file_path, timeout=15):
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

    def play_audio_file(self, audio_path, speed=1.0, quality=1, volume=None):
        """
        Centralized function to play audio files using afplay with enhanced settings to prevent word skipping
        """
        import time
        
        # Check if the audio file exists and is completely written
        if not self.wait_for_file_write_complete(audio_path):
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