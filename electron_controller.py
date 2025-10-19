import subprocess
import os
import socket
import threading
import json

class ElectronController:
    def __init__(self):
        self.electron_process = None
        self.socket_path = "/tmp/optimus-electron-socket"
        self.socket_server = None  # No longer used; kept for backward compatibility
        self.socket_thread = None  # No longer used; kept for backward compatibility
        self.is_listening = False  # No longer used; kept for backward compatibility
        
    def start_electron_app(self):
        """Start the Electron application"""
        try:
            # Ensure any stale socket owned by a previous Electron run is removed
            if os.path.exists(self.socket_path):
                try:
                    os.remove(self.socket_path)
                except Exception:
                    # If removal fails, we'll let Electron handle/replace it
                    pass
            
            # Start Electron app in the background
            self.electron_process = subprocess.Popen(
                ['npx', 'electron', 'main.js'],
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for Electron to create and listen on the Unix socket
            self._wait_for_socket_ready(timeout_seconds=10)
            
            print("🚀 Electron app started successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to start Electron app: {e}")
            return False
    
    def stop_electron_app(self):
        """Stop the Electron application"""
        if self.electron_process:
            try:
                # Send stop command
                self._send_command("stop")
                
                # Terminate the process
                self.electron_process.terminate()
                self.electron_process.wait(timeout=5)
                print("⏹️ Electron app stopped successfully")
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate gracefully
                self.electron_process.kill()
                print("⏹️ Electron app force killed")
            except Exception as e:
                print(f"❌ Error stopping Electron app: {e}")
        
        # Clean up socket file
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

    def _wait_for_socket_ready(self, timeout_seconds: int = 10):
        """Wait until the Electron socket is created and accepting connections."""
        import time

        deadline = time.time() + timeout_seconds
        last_error: Exception | None = None

        while time.time() < deadline:
            # Ensure the path exists first
            if os.path.exists(self.socket_path):
                try:
                    test_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    test_sock.settimeout(0.25)
                    test_sock.connect(self.socket_path)
                    test_sock.close()
                    return True
                except Exception as e:
                    last_error = e
            time.sleep(0.1)

        if last_error:
            print(f"⚠️ Socket not ready in time: {last_error}")
        else:
            print("⚠️ Socket path not created in time")
        return False
    
    def _send_command(self, command):
        """Send a command to the Electron app via socket"""
        try:
            # Best-effort quick connect; if it fails, retry briefly
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect(self.socket_path)
            sock.sendall(command.encode('utf-8'))
            sock.close()
            return True
        except Exception as e:
            # One short retry after a brief delay in case Electron just started listening
            try:
                import time
                time.sleep(0.2)
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                sock.connect(self.socket_path)
                sock.sendall(command.encode('utf-8'))
                sock.close()
                return True
            except Exception as e2:
                print(f"Failed to send command: {e2}")
                return False
    
    def play_animation(self):
        """Send play animation command to Electron app"""
        try:
            # For now, we'll just print a message
            # A more robust solution would use a proper IPC mechanism
            print("▶️ Playing animation")
            self._send_command("play")
            return True
        except Exception as e:
            print(f"❌ Failed to play animation: {e}")
            return False
    
    def pause_animation(self):
        """Send pause animation command to Electron app"""
        try:
            # For now, we'll just print a message
            # A more robust solution would use a proper IPC mechanism
            print("⏸️ Pausing animation")
            self._send_command("pause")
            return True
        except Exception as e:
            print(f"❌ Failed to pause animation: {e}")
            return False
    
    def show_summary_popup(self, summary):
        """Send a command to show a summary popup in the Electron app"""
        try:
            # Create a command that includes the summary text
            # Limit the summary length to prevent issues with the socket
            truncated_summary = summary[:2000]  # Increase the limit for more content
            command = f"show_summary {truncated_summary}"
            result = self._send_command(command)
            return result
        except Exception as e:
            print(f"❌ Failed to show summary popup: {e}")
            return False