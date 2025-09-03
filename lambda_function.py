import boto3
from pydub import AudioSegment
import os
import zipfile
import io
import json

os.environ["PATH"] += os.pathsep + os.path.dirname(os.path.abspath(__file__))

s3 = boto3.client('s3')

EXPECTED_API_KEY = os.environ.get('API_KEY')

def lambda_handler(event, context):
    try:
        api_key = event['headers'].get('x-api-key')
        if api_key != EXPECTED_API_KEY:
            return {
                'statusCode': 403,
                'body': json.dumps({'message': 'Forbidden: Invalid API Key'})
            }
        
        body = json.loads(event['body'])
        
        bucket_name = 'dubla-ai'
        output_key = body['output_key']
        keys = body['keys']
        merge_type = body.get('type', 'unified')
        
        if merge_type == 'zip':
            return create_zip(bucket_name, keys, output_key)
        elif merge_type == 'unified':
            return create_unified_audio(bucket_name, keys, output_key)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': f'Invalid type specified: {merge_type}. Expected "zip" or "unified".'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }

def create_zip(bucket_name, keys, output_key):
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for key in keys:
            download_path = f'/tmp/{os.path.basename(key)}'
            s3.download_file(bucket_name, key, download_path)
            zip_file.write(download_path, os.path.basename(key))

    zip_buffer.seek(0)

    s3.put_object(Bucket=bucket_name, Key=output_key, Body=zip_buffer.getvalue())

    return {
        'statusCode': 200,
        'body': json.dumps({'message': f'Successfully created ZIP file and uploaded to {output_key}', 'output_key': output_key})
    }

def create_unified_audio(bucket_name, keys, output_key):
    audio_segments = []
    for key in keys:
        download_path = f'/tmp/{os.path.basename(key)}'
        s3.download_file(bucket_name, key, download_path)
        audio_segments.append(AudioSegment.from_mp3(download_path))

    combined = sum(audio_segments)

    combined_path = '/tmp/combined.mp3'
    combined.export(combined_path, format="mp3", bitrate="128k")

    s3.upload_file(combined_path, bucket_name, output_key)

    return {
        'statusCode': 200,
        'body': json.dumps({'message': f'Successfully combined files and uploaded to {output_key}', 'output_key': output_key})
    }
