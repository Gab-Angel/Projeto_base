import base64
import os
from typing import Union

import requests
from dotenv import load_dotenv

load_dotenv()
bearer = os.getenv('BEARER_AUDIO_TRANSCRIPTION')


def audio_transcription(audio_data: Union[bytes, str]) -> dict:
    """
    Transcreve áudio usando Groq Whisper.
    
    Args:
        audio_data: Pode ser bytes ou string base64
    
    Returns:
        dict: Resultado da transcrição com chave 'text'
    """
    # Se for string base64, decodifica
    if isinstance(audio_data, str):
        audio_bytes = base64.b64decode(audio_data)
    else:
        audio_bytes = audio_data
    
    # Salva em arquivo temporário
    with open('temp_audio.mp3', 'wb') as f:
        f.write(audio_bytes)

    # Envia para transcrição
    headers = {
        'Authorization': f'Bearer {bearer}',
    }

    files = {
        'file': open('temp_audio.mp3', 'rb'),
        'model': (None, 'whisper-large-v3-turbo'),
        'language': (None, 'pt'),
    }

    response = requests.post(
        'https://api.groq.com/openai/v1/audio/transcriptions',
        headers=headers,
        files=files,
    )
    
    result = response.json()
    
    # Debug
    print(f"📊 Status da transcrição: {response.status_code}")
    print(f"📝 Resposta da API: {result}")
    
    return result