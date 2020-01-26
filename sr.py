import speech_recognition as sr

r = sr.Recognizer()


def rec_speech(filename: str, lang_code: str) -> str:
    audio_file = sr.AudioFile(filename)
    with audio_file as source:
        audio = r.record(source)
    full_text = r.recognize_google(audio, language=lang_code)
    print(f"full_text: {full_text}")
    return full_text