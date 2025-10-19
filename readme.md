✦ Optimus Prime Voice Assistant

  🤖 Transform and Roll Out! - A feature-rich voice assistant for macOS with AI
  capabilities and 3D animations.

  ![Python (https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
  ![License (https://img.shields.io/badge/License-MIT-green)](LICENSE)
  ![Platform 
  (https://img.shields.io/badge/Platform-macOS-lightgrey)](https://apple.com/macos)

  🚀 Overview

  Optimus Prime Voice Assistant is an advanced voice-controlled assistant for macOS that
  combines natural language processing, computer vision, and 3D animations. Built with
  Python, this project demonstrates modern AI/ML capabilities including speech
  recognition, text-to-speech synthesis, OCR, and local NLP processing.

  ✨ Features

   - Voice Commands: Control your system hands-free with natural language
   - App Management: Open and close applications using voice commands
   - Music Control: Play songs from your local music library
   - WhatsApp Integration: Send messages via voice commands
   - File Operations: Copy, move, delete, and navigate files
   - Apple Vision OCR: High-accuracy text recognition from images
   - Screen Summarization: Automatically analyze and summarize screen content
   - Education Portal Marks Monitoring: Track academic performance
   - 3D Animations: Visual feedback with Electron-powered 3D models
   - Local NLP Processing: Privacy-first AI with Ollama and Mistral model
   - Real-time Chat: Interactive chat interface with contextual understanding

  🛠️ Tech Stack

  Backend
   - Python 3.8+
   - SpeechRecognition - Speech-to-text conversion
   - TTS - Text-to-speech with voice cloning
   - PyAudio - Audio processing
   - PyObjC - Native macOS integration
   - LangChain - LLM orchestration
   - LangChain-Ollama - Local LLM integration
   - PyAutoGUI - System automation
   - Psutil - System resource monitoring

  AI/ML Models
   - Mistral:instruct via Ollama - Local NLP processing
   - YourTTS - Voice cloning and synthesis
   - Apple Vision Framework - OCR capabilities

  Frontend
   - Electron.js - Cross-platform desktop application
   - HTML/CSS/JavaScript - User interface
   - Sketchfab 3D Models - Animated visual feedback

  📋 Prerequisites

   - macOS 10.15+
   - Python 3.8 or higher
   - Node.js and npm (for Electron interface)
   - Access to microphone and speakers

  🚀 Installation

   1. Clone the repository

   1    git clone https://github.com/yourusername/optimus-prime-voice-assistant.git
   2    cd optimus-prime-voice-assistant

   2. Install Python dependencies

   1    pip install -r requirements.txt

   3. Install Ollama (for local NLP processing)

   1    # Follow instructions at https://ollama.ai/
   2    # Then pull the required model:
   3    ollama pull mistral:instruct

   4. Install Node.js dependencies

   1    cd chat_box
   2    npm install

   5. Set up required audio file
      - Place optimus-clear_nZx1aJFy.wav in the root directory for TTS voice cloning

  🎮 Usage

  Quick Start

   1 python main_assistant.py

  Voice Commands
   - "Open WhatsApp for me" - Launch WhatsApp
   - "Close Safari" - Quit Safari
   - "Launch Visual Studio Code" - Open VS Code
   - "Play Bohemian Rhapsody" - Play music
   - "Message John with Hello there" - Send WhatsApp message
   - "Summarize screen" - Analyze and summarize current screen
   - "Monitor marks" - Start marks monitoring system
   - "Close chat box" - Open interactive chat interface
   - "Transform Optimus" - Shutdown assistant

  Command Line Interface

    1 # Open specific application
    2 python app_launcher.py "Safari"
    3 
    4 # Play music
    5 python app_launcher.py "play Bohemian Rhapsody"
    6 
    7 # Send WhatsApp message
    8 python app_launcher.py "message John with Hello there"
    9 
   10 # Monitor marks
   11 python app_launcher.py "monitor marks"

  🔧 Key Modules

  main_assistant.py
  Core application loop with audio management and command processing.

  speech_to_text.py
  Advanced speech recognition using Google's API with local audio processing.

  text_to_speech.py
  Voice synthesis with custom Optimus Prime voice cloning using YourTTS model.

  command_processor.py
  Natural language processing for interpreting user commands and executing actions.

  app_launcher.py
  Application management and system integration functions.

  functions/ocr_detection.py
  Apple Vision Framework OCR for high-accuracy text detection from images.

  functions/screen_summarizer.py
  Screen capture and content summarization using OCR and local LLM.

  functions/marks_monitor.py
  Academic performance tracking for education portal integration.

  chat_box/
  Electron application with 3D animations and chat interface.

  🤖 NLP Capabilities

  The assistant uses Ollama with the Mistral:instruct model running locally on your
  machine for privacy-first natural language understanding. The system can:

   - Understand complex voice commands
   - Extract entities from natural language
   - Maintain conversation context
   - Process tabular data requests
   - Generate contextual responses

  📷 OCR Features

  The system leverages Apple's Vision Framework for OCR capabilities, providing excellent
  accuracy in detecting text from images. This enables:

   - Screen text extraction and summarization
   - Document analysis and processing
   - Image-to-text conversion with high precision

  🎯 Use Cases

   - Productivity: Control your macOS system hands-free
   - Accessibility: Voice-based interaction for users with mobility needs
   - Multitasking: Keep your hands on the keyboard while managing applications
   - Education: Monitor academic performance through the education portal integration
   - Content Analysis: Extract and summarize information from visual content

  🐛 Known Issues

   - Music playback may interfere with microphone input
   - Some macOS permissions may require manual configuration
   - TTS model loading may take time on first run

  🤝 Contributing

  Contributions are welcome! Please follow these steps:

   1. Fork the repository
   2. Create a feature branch (git checkout -b feature/amazing-feature)
   3. Commit your changes (git commit -m 'Add amazing feature')
   4. Push to the branch (git push origin feature/amazing-feature)
   5. Open a Pull Request

  📄 License

  This project is licensed under the MIT License - see the LICENSE (LICENSE) file for
  details.

  🙏 Acknowledgments

   - SpeechRecognition library for voice input handling
   - Coqui TTS for voice synthesis capabilities
   - Apple Vision Framework for OCR functionality
   - Ollama for local LLM access
   - Electron for cross-platform desktop application development