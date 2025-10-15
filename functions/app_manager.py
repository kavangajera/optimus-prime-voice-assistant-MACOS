import subprocess

class AppManager:
    def __init__(self):
        pass

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

    def close_app(self, app_name):
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

    def list_available_apps(self):
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
