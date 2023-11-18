import requests # To make HTTP requests
import json # To format HTTP headers/parameters
import soundfile as sf
import numpy as np
import os
from pydub import AudioSegment
import io
import moviepy.audio.fx.all as mp_audio
import moviepy.editor as mp

def generate_music(destination: str, prompt: str = "instagram tech video background music"):
    API_URL = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
    headers = {"Authorization": f"Bearer {os.environ["HuggingFaceAPIKey"]}"}
    params = json.dumps({
        "inputs": prompt, 
        "options": {
            "wait_for_model": True, 
            "top_p": 10, 
            "top_k": 10
        }
    })
    response = requests.post(API_URL, headers=headers, data=params)
    if response.status_code == 200:
        audio_flac = response.content
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_flac), format="flac")
        wav_audio = audio_segment.set_frame_rate(44100).set_channels(1)
        wav_audio.export(f"{destination}-temp1.wav", format="wav")
    else:
        print(f"Error: {response.status_code}, {response.text}")
    
    response = requests.post(API_URL, headers=headers, data=params)
    if response.status_code == 200:
        audio_flac = response.content
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_flac), format="flac")
        wav_audio = audio_segment.set_frame_rate(44100).set_channels(1)
        wav_audio.export(f"{destination}-temp2.wav", format="wav")
    else:
        print(f"Error: {response.status_code}, {response.text}")
    
    audio1 = mp_audio.auidio_fadeout(mp.AudioFileClip(f"{destination}-temp1.wav"), 2)
    audio2 = mp_audio.auidio_fadein(mp.AudioFileClip(f"{destination}-temp2.wav"), 2)
    combined_audio = mp.concatenate_audioclips([audio1, audio2])
    combined_audio.write_audiofile(f"{destination}.wav")
    os.remove(f"{destination}-temp1.wav")
    os.remove(f"{destination}-temp2.wav")
