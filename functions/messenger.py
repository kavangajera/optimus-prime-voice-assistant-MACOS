import subprocess
import time

class Messenger:
    def __init__(self):
        pass

    def send_whatsapp_message(self, contact_name, message):
        """Send a message to a WhatsApp contact"""
        try:
            # Check if WhatsApp is already running
            was_running = self.is_app_running("WhatsApp")

            # Open WhatsApp
            if not was_running:
                if not self.open_app("WhatsApp"):
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

    def is_app_running(self, app_name):
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

    def open_app(self, app_name):
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
