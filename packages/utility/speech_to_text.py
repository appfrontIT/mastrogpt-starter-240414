#--web true
#--kind python:default
#--annotation description "This action transalte audio to text"
#--timeout 300000
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation url https://nuvolaris.dev/api/v1/web/gporchia/utility/speech_to_text

from openai import OpenAI
import base64
from io import BytesIO

def main(args):
    # print(args)
    audio = args.get('__ow_body', None)
    if not audio:
        return {"statusCode": 404, "body": "audio not found"}
    decoded = base64.b64decode(audio)

    client = OpenAI(api_key=args['OPENAI_API_KEY'])
    # audio_file = open(audio, "rb")
    wav_file = open("temp.wav", "wb")
    wav_file.write(decoded)
    wav_file.close()
    audio_file = open("temp.wav", "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file,
        response_format="text"
        )
    return {"statusCode": 200, "body": transcription}