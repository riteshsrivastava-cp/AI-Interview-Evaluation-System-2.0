from gtts import gTTS
from playsound import playsound
import os
import time

def speak(text):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_file = os.path.join(base_dir, "feedback.mp3")

    obj = gTTS(text=text, lang="en", slow=False)
    obj.save(audio_file)

    print(audio_file)
    print(os.path.exists(audio_file))

    time.sleep(0.5)

    playsound(audio_file)

