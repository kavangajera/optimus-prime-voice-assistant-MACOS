import sys
from functions.app_manager import AppManager
from functions.music_controller import MusicController
from functions.messenger import Messenger
from functions.marks_monitor import MarksMonitor
from functions.safari_searcher import SafariSearcher


def main():
    app_manager = AppManager()
    music_controller = MusicController()
    messenger = Messenger()
    marks_monitor = MarksMonitor()
    safari_searcher = SafariSearcher()

    if len(sys.argv) > 1:
        # If app name is provided as command line argument
        app_name = " ".join(sys.argv[1:])
        # Check if it's a music command
        if app_name.lower().startswith("play "):
            song_name = app_name[5:]  # Remove "play " prefix
            if music_controller.play_music(song_name):
                music_controller.monitor_music_playback()
        # Check if it's a WhatsApp message command
        elif app_name.lower().startswith("message "):
            # Extract contact and message from command
            # Format: "message contact_name with Hello there"
            parts = app_name[8:].split(" with ")
            if len(parts) == 2:
                contact_name = parts[0]
                message = parts[1]
                messenger.send_whatsapp_message(contact_name, message)
            else:
                print("❌ Invalid message format. Use: message contact_name with your_message")
        elif app_name.lower() == "monitor marks":
            marks_monitor.start_monitor_marks()
        elif app_name.lower() == "stop monitoring marks":
            marks_monitor.stop_monitor_marks()
        else:
            app_manager.open_app(app_name)
    else:
        # Interactive mode
        print("🚀 App Launcher for macOS")
        print("=" * 30)

        app_manager.list_available_apps()

        print("\n💡 Usage:")
        print("  - Run with app name: python app_launcher.py \"App Name\"")
        print("  - Play music: python app_launcher.py \"play Song Name\"")
        print("  - Send WhatsApp message: python app_launcher.py \"message Contact Name with Your message\"")
        print("  - Monitor marks: python app_launcher.py \"monitor marks\"")
        print("  - Stop monitoring marks: python app_launcher.py \"stop monitoring marks\"")
        print("  - Run interactively: python app_launcher.py")

        print("\n📋 Enter the name of the application you want to open, 'play Song Name' to play music, 'message Contact Name with Your message' to send a WhatsApp message, 'monitor marks' to start marks monitoring, or 'stop monitoring marks' to stop it:")
        user_input = input("> ")

        if "quit" in user_input.lower():
            app_manager.close_app(user_input.replace("quit", "").strip())
        elif user_input.lower().startswith("play "):
            song_name = user_input[5:]  # Remove "play " prefix
            music_controller.play_music(song_name)
        elif user_input.lower().startswith("message "):
            # Extract contact and message from command
            # Format: "message contact_name with Hello there"
            parts = user_input[8:].split(" with ")
            if len(parts) == 2:
                contact_name = parts[0]
                message = parts[1]
                messenger.send_whatsapp_message(contact_name, message)
            else:
                print("❌ Invalid message format. Use: message contact_name with your_message")
        elif user_input.lower() == "monitor marks":
            marks_monitor.start_monitor_marks()
        elif user_input.lower() == "stop monitoring marks":
            marks_monitor.stop_monitor_marks()
        elif user_input.strip():
            app_manager.open_app(user_input)
        else:
            print("❌ No application name provided.")


# Global functions for external use
def open_app(app_name):
    """Open an application"""
    app_manager = AppManager()
    return app_manager.open_app(app_name)

def close_app(app_name):
    """Close an application"""
    app_manager = AppManager()
    return app_manager.close_app(app_name)

def play_music(song_name):
    """Play music"""
    music_controller = MusicController()
    return music_controller.play_music(song_name)

def send_whatsapp_message(contact_name, message):
    """Send WhatsApp message"""
    messenger = Messenger()
    return messenger.send_whatsapp_message(contact_name, message)

def monitor_music_playback():
    """Monitor music playback"""
    music_controller = MusicController()
    return music_controller.monitor_music_playback()

def start_monitor_marks():
    """Start marks monitoring"""
    marks_monitor = MarksMonitor()
    return marks_monitor.start_monitor_marks()

def stop_monitor_marks():
    """Stop marks monitoring"""
    marks_monitor = MarksMonitor()
    return marks_monitor.stop_monitor_marks()

def open_chatbox():
    """Open the chatbox application"""
    import subprocess
    try:
        # Run the Electron app for the chatbox from the test_files directory
        subprocess.Popen(["npm", "start"], cwd="./test_files", shell=False)
        return True
    except Exception as e:
        print(f"Error opening chatbox: {e}")
        return False

def close_chatbox():
    """Close the chatbox application"""
    import subprocess
    import os
    import signal
    import psutil
    import time
    try:
        # Find and kill Electron processes that are running the table view (not the main optimus app)
        for proc in psutil.process_iter():
            try:
                # Check if the process name contains "Electron" and the command line includes the test_files directory
                if "Electron" in proc.name() and "./test_files" in " ".join(proc.cmdline()):
                    # Check if this is the main optimus process or just the table view
                    cmdline = " ".join(proc.cmdline())
                    # If it's the table view, it would likely have different characteristics
                    # Let's find processes that are running in test_files directory but not the main index.html
                    if "json_to_table.html" in cmdline or "json_to_table" in cmdline or "table" in cmdline.lower():
                        proc.kill()
                        print(f"Killed table view process: {proc.pid}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Handle potential errors during process enumeration
                pass
        return True
    except Exception as e:
        print(f"Error closing chatbox: {e}")
        return False

def search_safari(query):
    """Search in Safari"""
    safari_searcher = SafariSearcher()
    return safari_searcher.search_in_safari(query)

if __name__ == "__main__":
    main()