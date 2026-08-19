import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np



def record_audio():
    fs = 44100

    input("Press Enter to start recording...")

    recording = []

    def callback(indata, frames, time, status):
        recording.append(indata.copy())

    stream = sd.InputStream(
        samplerate=fs,
        channels=1,
        callback=callback
    )

    stream.start()


    input("Recording... Press Enter to stop.")

    stream.stop()
    stream.close()

    # import numpy as np
    audio = np.concatenate(recording, axis=0)

    write("recording.wav", fs, audio)

    print("Recording saved!")
    return 'recording.wav'

