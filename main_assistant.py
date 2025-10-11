import time
# Import our custom modules
from speech_to_text import listen_for_command
# Import our new modules
from audio_handler import AudioHandler
from tts_handler import TTSHandler
from command_processor import CommandProcessor
from system_optimizer import SystemOptimizer
# Import Electron controller
from electron_controller import ElectronController


def main():
    """
    Main voice assistant loop with optimized performance
    """
    # Optimize system performance first
    SystemOptimizer.optimize_system_performance()
    
    # Initialize audio handler for audio-related functionality
    audio_handler = AudioHandler()
    
    # Initialize Electron controller
    electron_controller = ElectronController()
    
    # Start Electron app    
    if not electron_controller.start_electron_app():
        print("❌ Failed to start 3D animation. Continuing without it.")
    
    # Initialize TTS handler with the audio handler
    tts_handler = TTSHandler(audio_handler)
    
    # Initialize command processor with needed handlers
    command_processor = CommandProcessor(audio_handler, tts_handler, electron_controller)
    
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
    tts_handler.speak_text_clean(welcome_msg, electron_controller)
    
    # Track time since last user interaction
    last_interaction_time = time.time()
    inactivity_timeout = 2  # Reduced timeout for quicker animation pause
    resource_check_counter = 0
    
    # Main listening loop with improved performance
    while True:
        # Monitor system resources periodically
        resource_check_counter += 1
        if resource_check_counter % 20 == 0:  # Check every 20 iterations
            system_ok = SystemOptimizer.monitor_system_resources()
            if not system_ok:
                time.sleep(0.2)  # Longer delay if system is under load
            else:
                time.sleep(0.05)  # Normal delay
        else:
            time.sleep(0.05)
        
        # Handle listening based on current state (TTS vs music vs normal)
        if audio_handler.is_audio_playing.is_set():
            # During TTS playback, microphone is managed by the TTS functions
            # We still attempt to listen but with caution
            command = None
            try:
                # Try to listen with shorter timeout during TTS
                command = listen_for_command()
            except:
                pass
        elif audio_handler.is_music_playing.is_set():
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
        
        if not command_processor.process_command(command):
            break
            
        # Update last interaction time if a command was received
        if command is not None:
            last_interaction_time = time.time()

if __name__ == "__main__":
    main()