import os

import requests
from dotenv import load_dotenv

load_dotenv()


# CONEXÃO COM EVOLUTION
base_url_evo = os.getenv('BASE_URL_EVO')
instance_token = os.getenv('API_KEY_EVO')
instance_name = os.getenv('INSTANCE_NAME')

url_sendText = f'{base_url_evo}/message/sendText/{instance_name}'
url_sendMedia = f'{base_url_evo}/message/sendMedia/{instance_name}'
headers = {'Content-Type': 'application/json', 'apikey': instance_token}


class EvolutionAPI:
    def __init__(self):
        self.base_url_evo = base_url_evo
        self.instance_name = instance_name
        self.headers = headers

    def _post(self, endpoint: str, payload: dict) -> dict:
        url = f'{self.base_url_evo}{endpoint}/{self.instance_name}'
        response = requests.post(url=url, headers=self.headers, json=payload)

        response.raise_for_status()
        return response.json()

    def sender_text(self, number: str, text: str) -> list[dict]:

        texto = text.replace('\n\n', ' ').replace('\n', ' ').strip()

        if '.' in texto:
            partes = texto.split('.')
        elif '!' in texto:
            partes = texto.split('!')
        else:
            partes = [texto]

        partes = [p.strip() for p in partes if p.strip()]

        responses = []

        for parte in partes:
            payload = {
                'number': number,
                'text': parte,
                'delay': 2000,
                'presence': 'composing',
            }

            response = self._post(
                endpoint='/message/sendText', payload=payload
            )

            responses.append(response)

        return responses

    def sender_file(
        self,
        numero: str,
        media_type: str,
        file_name: str,
        media: str,
        caption: str = '',
    ) -> dict:

        payload = {
            'number': numero,
            'mediatype': media_type,
            'fileName': file_name,
            'media': media,
            'caption': caption,
            'delay': 2000,
            'presence': 'composing',
        }

        return self._post(endpoint='/message/sendMedia', payload=payload)
