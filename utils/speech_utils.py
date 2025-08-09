# utils/speech_utils.py

import speech_recognition as sr
import pyttsx3

# Initialize the text-to-speech engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 170)  # Speaking speed
tts_engine.setProperty('volume', 1.0)  # Max volume


def speak_text(text):
    """
    Convert given text to speech.
    """
    try:
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        print(f"Error in TTS: {e}")


def listen_speech(timeout=5, phrase_time_limit=10):
    """
    Convert user's speech to text.
    - timeout: Seconds to wait before assuming no speech.
    - phrase_time_limit: Max seconds for a single speech input.
    """
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    try:
        with mic as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

        # Recognize speech using Google Speech Recognition API
        text = recognizer.recognize_google(audio)
        print(f"User said: {text}")
        return text

    except sr.WaitTimeoutError:
        print("No speech detected within timeout.")
        return None
    except sr.UnknownValueError:
        print("Speech was not clear enough to understand.")
        return None
    except sr.RequestError:
        print("Speech recognition service is unavailable.")
        return None
    except Exception as e:
        print(f"Error in STT: {e}")
        return None
