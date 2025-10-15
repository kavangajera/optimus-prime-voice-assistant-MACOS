import subprocess
import time

class MusicController:
    def __init__(self):
        pass

    def is_music_playing(self):
        """Check if music is currently playing in the Music app"""
        try:
            script = '''
            tell application "Music"
                if player state is playing then
                    return "playing"
                else
                    return "stopped"
                end if
            end tell
            '''

            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True, check=True)

            return result.stdout.strip() == "playing"
        except:
            return False

    def get_current_track_duration(self):
        """Get the duration of the current track in seconds"""
        try:
            script = '''
            tell application "Music"
                if player state is playing then
                    return duration of current track
                else
                    return 0
                end if
            end tell
            '''

            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True, check=True)

            duration = result.stdout.strip()
            if duration and duration.isdigit():
                return int(duration)
            return 0
        except:
            return 0

    def get_current_track_position(self):
        """Get the current playback position in seconds"""
        try:
            script = '''
            tell application "Music"
                if player state is playing then
                    return player position
                else
                    return 0
                end if
            end tell
            '''

            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True, check=True)

            position = result.stdout.strip()
            if position and position.replace('.', '').isdigit():
                return float(position)
            return 0
        except:
            return 0

    def play_music(self, song_name):
        """Play a specific song in Music app using AppleScript with optimized settings"""
        try:
            # AppleScript to search and play a song in Music app
            # Optimized for better performance and reliability
            script = f'''
            tell application "Music"
                activate
                delay 0.5
                try
                    set foundTracks to (every track of playlist "Library" whose name contains "{song_name}")
                    if (count of foundTracks) > 0 then
                        play item 1 of foundTracks
                        return "success"
                    else
                        return "not found"
                    end if
                on error
                    return "error"
                end try
            end tell
            '''

            # Run the script and capture output
            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True, check=True)

            if result.stdout.strip() == "success":
                print(f"🎵 Successfully playing '{song_name}' in Music app")
                return True
            elif result.stdout.strip() == "not found":
                print(f"❌ Song '{song_name}' not found in your library")
                return False
            else:
                print(f"❌ Error playing '{song_name}'")
                return False

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to play '{song_name}'. Error: {e}")
            return False
        except FileNotFoundError:
            print("❌ 'osascript' command not found. This script is designed for macOS.")
            return False
        except Exception as e:
            print(f"❌ Unexpected error playing music: {e}")
            return False

    def monitor_music_playback(self):
        """Monitor music playback and return when music stops"""
        # Wait until music is actually playing
        max_wait_time = 5  # Wait up to 5 seconds for music to start
        wait_time = 0
        while wait_time < max_wait_time:
            if self.is_music_playing():
                break
            time.sleep(0.5)
            wait_time += 0.5

        # Now monitor for when music stops
        while self.is_music_playing():
            time.sleep(1)  # Check every second
        print("🎵 Music playback finished")
