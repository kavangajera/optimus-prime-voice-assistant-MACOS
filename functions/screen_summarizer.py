import sys
from pathlib import Path
import tempfile
import subprocess

# Handle import for both direct run and package import
try:
    # For when this module is run as part of the package
    from .ocr_detection import ocr_mac
except ImportError:
    # For when this module is run directly
    from ocr_detection import ocr_mac

from chat_box.chat_service import ChatService


def capture_screen_and_summarize():
    """
    Captures the current screen, performs OCR to extract text,
    and generates a summary using the chat service.
    """
    # Create a temporary file for the screenshot
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        screenshot_path = temp_file.name
    
    try:
        # Capture the screen using macOS screenshot command
        result = subprocess.run([
            'screencapture', '-x', screenshot_path
        ], check=True, capture_output=True, text=True)
        
        # Perform OCR on the captured image
        extracted_text = ocr_mac(screenshot_path, recognition_level="accurate", languages=["en-US"])
        
        if not extracted_text.strip():
            return "No text found in the current screen."
        
        # Generate summary using the chat service
        chat_service = ChatService()
        summary_prompt = f"""Please provide a concise summary of the following text extracted from an image: 
                         Not only summarize, but also highlight key points and important details.
                         Answer in clear and structured format , point-wise if possible.
                         Extracted text: {extracted_text}"""
        summary = chat_service.ask_for_summary(summary_prompt)
        
        return summary
        
    except subprocess.CalledProcessError as e:
        return f"Error capturing screen: {e}"
    except Exception as e:
        return f"Error in screen summarization: {e}"
    finally:
        # Clean up temporary file
        try:
            import os
            os.remove(screenshot_path)
        except:
            pass


if __name__ == "__main__":
    summary = capture_screen_and_summarize()
    print(summary)