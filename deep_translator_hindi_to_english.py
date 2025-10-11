from deep_translator import GoogleTranslator
import speech_recognition as sr

def translate_to_english(text):
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        return translated
    except Exception as e:
        print(f"❌ Translation error: {e}")
        return text  # fallback to original

def listen_for_command():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    with mic as source:
        print("🎙️ Speak now...")
        audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
    
    try:
        # Recognize Hindi speech
        text = recognizer.recognize_google(audio, language="hi-IN")
        print(f"🗣️ Detected (Hindi): {text}")

        # Translate to English
        translated = translate_to_english(text)
        print(f"🌐 Translated (English): {translated}")

        return translated.lower()
    
    except sr.UnknownValueError:
        print("🔇 Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"⚠️ API Error: {e}")
        return None
    
if __name__ == "__main__":
    while True:
        command = listen_for_command()
        if command:
            print(f"✅ Final Command: {command}")
        else:
            print("❌ No valid command detected.")
