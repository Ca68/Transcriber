import argparse

parser = argparse.ArgumentParser(prog='transcriber')
parser.add_argument('-i', help='Enter the URL of YouTube video')
args = parser.parse_args()

f = open("api.txt", "r")
api_key = f.read()

print('1. API is read...')

from pytube import YouTube
import os
video = YouTube(args.i)
yt = video.streams.get_audio_only()

yt.download()

current_dir = os.getcwd()

for file in os.listdir(current_dir):
    if file.endswith(".mp4"):
        mp4_file = os.path.join(current_dir, file)

print('2. Audio file has been retrieved from YouTube video')

import sys
import time
import requests

filename = mp4_file

def read_file(filename, chunk_size=5242880):
    with open(filename, 'rb') as _file:
        while True:
            data = _file.read(chunk_size)
            if not data:
                break
            yield data

headers = {'authorization': api_key}
response = requests.post('https://api.assemblyai.com/v2/upload',
                        headers = headers,
                        data = read_file(filename))

audio_url = response.json()['upload_url']

print('3. YouTube audio file has been uploaded to AssemblyAI')

import requests

endpoint = "https://api.assemblyai.com/v2/transcript"

json = {
    "audio_url": audio_url,
    "language_detection": True
}

headers = {
    "authorization": api_key,
    "content-type": "application/json"
}

transcript_input_response = requests.post(endpoint, json=json, headers=headers)

print('4. Transcribing uploaded file')

transcript_id = transcript_input_response.json()["id"]

print('5. Extract transcript ID')

endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
headers = {
    "authorization": api_key,
    
}

transcript_output_response = requests.get(endpoint, headers=headers)

print('6. Retrieve transcripion results')

from time import sleep

while transcript_output_response.json()['status'] != 'completed':
    sleep(20)
    print('Transcription is processing...')
    transcript_output_response = requests.get(endpoint, headers=headers)

print('---------\n')
print('Output:\n')
print(transcript_output_response.json()["text"])

yt_txt = open('yt.txt', 'w')
yt_txt.write(transcript_output_response.json()["text"])
yt_txt.close()

srt_endpoint = endpoint + "/srt"
srt_response = requests.get(srt_endpoint, headers=headers)

with open("yt.srt", "w") as _file:
    _file.write(srt_response.text)
