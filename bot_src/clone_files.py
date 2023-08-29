from pydub import AudioSegment
from src.text2speech.cloning_voice import voice_cloning

def customer_voice_cloning(id):
    voice_source = f'/kaggle/working/AI-avatar-generator/voice_message/{id}.mp3'
    audio_source = f'/kaggle/working/AI-avatar-generator/customer_files/customer_audio_source/{id}.wav'
    print(voice_source, audio_source)
    sound = AudioSegment.from_file(voice_source, 'ogg')
    sound.export(audio_source, format="wav")
    try:
        voice_cloning(id, audio_source)
        return True
    except:
        return False
