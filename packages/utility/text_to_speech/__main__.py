#--web true
#--kind python:default
#--annotation description "This action transalte text to audio"
#--timeout 300000
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation url https://walkiria.cloud/api/v1/web/{os.environ['__OW_NAMESPACE']}/utility/text_to_speech

from openai import OpenAI
import base64
import io

def main(args):
    text = args.get('__ow_body', None)
    if not text:
        return {"statusCode": 404, "body": "audio not found"}

    client = OpenAI(api_key=args['OPENAI_API_KEY'])
    
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
        response_format="mp3",
        )
    # buffer = io.BytesIO()
    # for chunk in response.iter_bytes(chunk_size=4096):
    #     buffer.write(chunk)
    # buffer.seek(0)
    decoded_string = response.read()
    return {"statusCode": 200, 'body': str(decoded_string)}