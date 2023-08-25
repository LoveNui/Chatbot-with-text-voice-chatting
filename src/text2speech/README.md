# Text to Speech Engine with Bark Model
## Setting Environment

    git clone https://gitlab.com/lambda-vision/customersupportgpt.git
    cd customersupportgpt/Bark_TTS
    pip install requirement.txt
## Generating voice - Bark_tts.py

### Usage
Import the function 'tts' in FastAPI_voice_generator.py

    `from Bark_TTS.Bark_tts import tts`
###### Parameters
- *text:* the text that needs to be converted to the speech
- *voice_name:* the voice name that is used to generate speech(This is the name of customer voice model)

###### Output
- audio stream

## Cloning customer voice - Bark_voice_cloning.py

### Usage
Import the function 'voice_cloning' in FastAPI_voice_generator.py

    `from Bark_TTS.Bark_voice_cloning import voice_cloning`
###### Parameters
- *cloned_speaker_name:* the name of the cloned customer voice
- *voice_source:* the customer voice source file path, This file have to be saved in "clone_voice_source"

###### Output
- save new npz file for customer voice in "clone_voice_tokens"
