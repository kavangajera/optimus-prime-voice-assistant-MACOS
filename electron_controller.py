import subprocess
import time
import os
import json
import socket
import threading

class ElectronController:
    def __init__(self):
        self.electron_process = None
        self.socket_path = "/tmp/optimus-electron-socket"
        self.socket_server = None
        self.socket_thread = None
        self.is_listening = False
        
    def start_electron_app(self):
        """Start the Electron application"""
        try:
            # Remove existing socket file if it exists
            if os.path.exists(self.socket_path):
                os.remove(self.socket_path)
            
            # Start Electron app in the background
            self.electron_process = subprocess.Popen(
                ['npx', 'electron', 'main.js'],
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Start socket server in a separate thread
            self.is_listening = True
            self.socket_thread = threading.Thread(target=self._start_socket_server, daemon=True)
            self.socket_thread.start()
            
            print("🚀 Electron app started successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to start Electron app: {e}")
            return False
    
    def stop_electron_app(self):
        """Stop the Electron application"""
        # Stop socket server
        self.is_listening = False
        
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
    
    def _start_socket_server(self):
        """Start a Unix socket server to receive commands"""
        try:
            self.socket_server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket_server.bind(self.socket_path)
            self.socket_server.listen(1)
            
            while self.is_listening:
                try:
                    connection, client_address = self.socket_server.accept()
                    try:
                        data = connection.recv(1024)
                        if data:
                            command = data.decode('utf-8')
                            # Process command here if needed
                            pass
                    finally:
                        connection.close()
                except Exception as e:
                    if self.is_listening:
                        print(f"Socket server error: {e}")
                        break
        except Exception as e:
            print(f"Failed to start socket server: {e}")
    
    def _send_command(self, command):
        """Send a command to the Electron app via socket"""
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.socket_path)
            sock.sendall(command.encode('utf-8'))
            sock.close()
            return True
        except Exception as e:
            print(f"Failed to send command: {e}")
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