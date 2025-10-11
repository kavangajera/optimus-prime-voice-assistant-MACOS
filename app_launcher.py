import subprocess
import sys
import time
import threading

def is_app_running(app_name):
    """Check if an application is currently running"""
    try:
        # Use 'osascript' to check if app is running with the correct AppleScript
        script = f'tell application \"System Events\" to (name of every process) contains \"{app_name}\"'
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, check=True)
        # If the output contains "true", the app is running
        return result.stdout.strip() == "true"
    except subprocess.CalledProcessError:
        return False
    except Exception:
        return False


def is_music_playing():
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


def get_current_track_duration():
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


def get_current_track_position():
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


def open_app(app_name):
    """Open an application on macOS"""
    try:
        # Use the 'open -a' command to open applications
        subprocess.run(['open', '-a', app_name], check=True)
        print(f"✅ Successfully opened {app_name}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to open {app_name}. Make sure the app name is correct.")
        return False
    except FileNotFoundError:
        print("❌ 'open' command not found. This script is designed for macOS.")
        return False


def close_app(app_name):
    """Close an application on macOS"""
    try:
        # Use the 'osascript' command to close applications
        script = f'tell application "{app_name}" to quit'
        subprocess.run(['osascript', '-e', script], check=True)
        print(f"✅ Successfully closed {app_name}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to close {app_name}. The app might already be closed or the name is incorrect.")
        return False
    except FileNotFoundError:
        print("❌ 'osascript' command not found. This script is designed for macOS.")
        return False


def send_whatsapp_message(contact_name, message):
    """Send a message to a WhatsApp contact"""
    try:
        # Check if WhatsApp is already running
        was_running = is_app_running("WhatsApp")
        
        # Open WhatsApp
        if not was_running:
            if not open_app("WhatsApp"):
                return False
            
        # Wait for WhatsApp to open
        time.sleep(3)
        
        # Determine number of down arrows based on whether WhatsApp was already running
        if was_running:
            print("WhatsApp was already running, using 1 down arrow to select contact.")
            # If WhatsApp was already running, use 1 down arrow
            down_arrows = 1
        else:
            print("WhatsApp was not running, using 2 down arrows to select contact.")
            # If WhatsApp was closed and is opened for first time, use 2 down arrows
            down_arrows = 2
        
        # Use AppleScript to search for contact and send message
        script = f'''
        tell application "WhatsApp"
            activate
        end tell
        delay 2
        tell application "System Events"
            -- Close the chat using Shift+Cmd+W
            keystroke "w" using {{shift down, command down}}
            delay 1
            -- Open search with Cmd+F
            keystroke "f" using {{command down}}
            delay 1
            -- Type contact name
            keystroke "{contact_name}"
            delay 2
            -- Press down arrow based on app state
            '''
        
        # Add the appropriate number of down arrows
        for _ in range(down_arrows):
            script += '''
            key code 125
            delay 0.5
            '''
        
        script += f'''
            -- Press return to open chat
            keystroke return
            delay 2
            -- Type the message
            keystroke "{message}"
            delay 1
            -- Send the message
            keystroke return
            delay 1
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        print(f"✅ Successfully sent message to {contact_name} and closed the chat")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to send message to {contact_name}")
        return False
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False


def play_music(song_name):
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


def monitor_music_playback():
    """Monitor music playback and return when music stops"""
    # Wait until music is actually playing
    max_wait_time = 5  # Wait up to 5 seconds for music to start
    wait_time = 0
    while wait_time < max_wait_time:
        if is_music_playing():
            break
        time.sleep(0.5)
        wait_time += 0.5
    
    # Now monitor for when music stops
    while is_music_playing():
        time.sleep(1)  # Check every second
    print("🎵 Music playback finished")


def list_available_apps():
    """List some common applications that can be opened"""
    common_apps = [
        "WhatsApp",
        "App Store",
        "Visual Studio Code",
        "Safari",
        "Mail",
        "Messages",
        "Calendar",
        "Notes",
        "Photos",
        "Music",
        "Maps",
        "System Settings"
    ]
    
    print("📱 Common applications you can open:")
    for i, app in enumerate(common_apps, 1):
        print(f"  {i}. {app}")


def main():
    if len(sys.argv) > 1:
        # If app name is provided as command line argument
        app_name = " ".join(sys.argv[1:])
        # Check if it's a music command
        if app_name.lower().startswith("play "):
            song_name = app_name[5:]  # Remove "play " prefix
            play_music(song_name)
        # Check if it's a WhatsApp message command
        elif app_name.lower().startswith("message "):
            # Extract contact and message from command
            # Format: "message contact_name with Hello there"
            parts = app_name[8:].split(" with ")
            if len(parts) == 2:
                contact_name = parts[0]
                message = parts[1]
                send_whatsapp_message(contact_name, message)
            else:
                print("❌ Invalid message format. Use: message contact_name with your_message")
        else:
            open_app(app_name)
    else:
        # Interactive mode
        print("🚀 App Launcher for macOS")
        print("=" * 30)
        
        list_available_apps()
        
        print("\n💡 Usage:")
        print("  - Run with app name: python app_launcher.py \"App Name\"")
        print("  - Play music: python app_launcher.py \"play Song Name\"")
        print("  - Send WhatsApp message: python app_launcher.py \"message Contact Name with Your message\"")
        print("  - Run interactively: python app_launcher.py")
        
        print("\n📋 Enter the name of the application you want to open, 'play Song Name' to play music, or 'message Contact Name with Your message' to send a WhatsApp message:")
        user_input = input("> ")

        if "quit" in user_input.lower():
            close_app(user_input.replace("quit", "").strip())
        elif user_input.lower().startswith("play "):
            song_name = user_input[5:]  # Remove "play " prefix
            play_music(song_name)
        elif user_input.lower().startswith("message "):
            # Extract contact and message from command
            # Format: "message contact_name with Hello there"
            parts = user_input[8:].split(" with ")
            if len(parts) == 2:
                contact_name = parts[0]
                message = parts[1]
                send_whatsapp_message(contact_name, message)
            else:
                print("❌ Invalid message format. Use: message contact_name with your_message")
        elif user_input.strip():
            open_app(user_input)
        else:
            print("❌ No application name provided.")

if __name__ == "__main__":
    main()