import whisper

# Model load 
model = whisper.load_model("base")


def speech_to_text(audio_file):
    # Audio ko text me convert
    result = model.transcribe(audio_file)

    # Text print 
    print(result["text"])

    return result["text"]

