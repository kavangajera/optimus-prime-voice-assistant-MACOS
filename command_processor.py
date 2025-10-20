"""
Command processing module for the Optimus Prime Voice Assistant
"""
import subprocess
import os
import re
import threading
import time
import re
import threading
import time
from app_launcher import open_app, close_app, play_music, monitor_music_playback, start_monitor_marks, stop_monitor_marks , search_safari, open_chatbox, close_chatbox, summarize_screen, start_bluetooth
from functions.messenger import Messenger
from speech_to_text import microphone_active
from text_to_speech import get_tts_instance
from functions.file_operations import perform_file_operation


class CommandProcessor:
    def __init__(self, audio_handler, tts_handler, electron_controller):
        self.audio_handler = audio_handler
        self.tts_handler = tts_handler
        self.electron_controller = electron_controller
        self.messenger = Messenger()

    def extract_music_command(self, command):
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

    def extract_app_name(self, command):
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

    def process_command(self, command):
        """
        Process the recognized voice command
        """
        if not command:
            # Pause animation when no command is received
            if self.electron_controller:
                self.electron_controller.pause_animation()
            return True  # Continue listening
        
        if "search safari for" in command.lower():
            search_query = command.lower().split("search safari for",1)[1].strip()
            response = f"Searching Safari for {search_query} sir!"
            print(f"🤖 {response}")
            self.tts_handler.speak_text_clean(response, self.electron_controller)
            success = search_safari(search_query)
            if not success:
                error_response = "I encountered an error while searching in Safari."
                self.tts_handler.speak_text_clean(error_response, self.electron_controller)
            return True  # Continue listening
        
        # Check for screen summarization command
        if "summarise screen" in command.lower() or "summarise current screen" in command.lower():
            response = "Summarizing image for you sir!"
            print(f"🤖 {response}")
            self.tts_handler.speak_text_clean(response, self.electron_controller)
            
            # Get summary from screen
            summary = summarize_screen()
            
            # Show the summary in a popup centered on the screen (like in index.html)
            self.show_summary_popup(summary)
            return True  # Continue listening
        
        # Check for monitor marks command
        if "monitor marks" in command.lower():
            response = "Starting marks monitoring system for you sir!"
            print(f"🤖 {response}")
            self.tts_handler.speak_text_clean(response, self.electron_controller)
            success = start_monitor_marks()
            if not success:
                error_response = "I encountered an error while starting the marks monitoring system."
                self.tts_handler.speak_text_clean(error_response, self.electron_controller)
            return True  # Continue listening

        # Check for stop monitoring marks command
        if "stop monitoring marks" in command.lower():
            response = "Stopping marks monitoring system for you sir!"
            print(f"🤖 {response}")
            self.tts_handler.speak_text_clean(response, self.electron_controller)
            success = stop_monitor_marks()
            if not success:
                response = "No active marks monitoring system is running."
                self.tts_handler.speak_text_clean(response, self.electron_controller)
            return True  # Continue listening

        # Check for start bluetooth command
        if "start bluetooth" in command.lower():
            response = "Starting Bluetooth and connecting to JBL Tune 520BT for you sir!"
            print(f"🤖 {response}")
            self.tts_handler.speak_text_clean(response, self.electron_controller)
            success = start_bluetooth()
            if not success:
                error_response = "I encountered an error while starting Bluetooth and connecting to JBL Tune 520BT."
                self.tts_handler.speak_text_clean(error_response, self.electron_controller)
            return True  # Continue listening

        
        # Check for exit command
        
        # Check for open chatbox command
        if "open chat box" in command.lower():
            response = "Opening chatbox for you sir!"
            print(f"🤖 {response}")
            self.tts_handler.speak_text_clean(response, self.electron_controller)
            open_chatbox()
            return True  # Continue listening
        
        # Check for close chatbox command
        if "close chat box" in command.lower():
            response = "Closing chatbox for you sir!"
            print(f"🤖 {response}")
            self.tts_handler.speak_text_clean(response, self.electron_controller)
            close_chatbox()
            return True  # Continue listening        if "transform optimus" in command.lower():
        
        # Check for exit command
        if "transform optimus" in command.lower():
            response = "Rollouting Sir! Good bye..."
            print(f"🤖 {response}")
            self.tts_handler.speak_text_clean(response, self.electron_controller)
            return False  # Stop listening
        
        # Check for music commands
        song_name = self.extract_music_command(command)
        if song_name:
            response = f"Playing {song_name} for you sir!"
            print(f"🤖 {response}")
            
            # Start music playback with proper TTS and timing
            def play_music_with_tts():
                # Set the music playing flag to prevent microphone from starting/stopping
                self.audio_handler.is_music_playing.set()
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
                        self.audio_handler.play_audio_file(output_path, speed=0.9, quality=1)
                    
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
                            self.audio_handler.play_audio_file(output_path, speed=1.0, quality=1)
    
                except Exception as e:
                    print(f"❌ Music playback error: {e}")
                finally:
                    # Always clear the music playing flag when music playback is done
                    self.audio_handler.is_music_playing.clear()
                    # Resume microphone after music playback
                    microphone_active.set()
                 
            
            # Start music with TTS in independent thread
            # No microphone control during this process
            music_thread = threading.Thread(target=play_music_with_tts, daemon=True)
            music_thread.start()
            
            return True
        
        # Check for file operations commands
        file_operation_keywords = [
            'copy', 'move', 'delete', 'create', 'paste', 'open', 'close', 'folder', 
            'directory', 'file', 'files', 'folders', 'directories', 'put', 'send', 
            'transfer', 'shift', 'erase', 'remove', 'trash', 'make', 'build', 'go to',
            'navigate to','rename', 'enter', 'downloads', 'documents', 'desktop', 'home', 'kavan'
        ]
        
        # Check if command contains file operation keywords
        if any(keyword in command.lower() for keyword in file_operation_keywords):
            # Process as file operation command
            try:
                result = perform_file_operation(command)
                
                # Check if this is a navigation command (returns a path instead of operation result)
                if result.startswith("Navigation path: "):
                    path = result.replace("Navigation path: ", "").strip()
                    response = f"Going to {path} for you, sir!"
                else:
                    response = f"{result}, sir!"
                
                print(f"🤖 {response}")
                self.tts_handler.speak_text_clean(response, self.electron_controller)
                return True
            except Exception as e:
                response = f"Error with file operation: {str(e)}, sir!"
                print(f"🤖 {response}")
                self.tts_handler.speak_text_clean(response, self.electron_controller)
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
            self.tts_handler.speak_text_clean(response, self.electron_controller)
            # Use the messenger's process_message_request instead of direct send_whatsapp_message
            result = self.messenger.process_message_request(command)
            print(f"Message result: {result}")
            return True
        
        # Extract app name and action from command
        action_info = self.extract_app_name(command)
        
        if action_info:
            action, app_name = action_info
            
            if action == "open":
                response = f"Opening {app_name} for you sir!"
                print(f"🤖 {response}")
                self.tts_handler.speak_text_clean(response, self.electron_controller)
                open_app(app_name)
            elif action == "close":
                response = f"Closing {app_name} for you sir!"
                print(f"🤖 {response}")
                self.tts_handler.speak_text_clean(response, self.electron_controller)
                close_app(app_name)
        else:
            response = "I didn't get the command sir. Please try to say it again."
            # print(f"🤖 {response}")
            self.tts_handler.speak_text_clean(response, self.electron_controller)
        
        return True  # Continue listening

    def show_summary_popup(self, summary):
        """
        Show a summary popup in the Electron application
        """
        if self.electron_controller:
            self.electron_controller.show_summary_popup(summary)
    

