import os
import ffmpeg
from flask import session


filename = session.get("filename")
file_type = session.get("file_type")

def video_to_mp3(mp4_file):
    output_file = "lecture_to_audio.mp3"
    ffmpeg.input(mp4_file).output(output_file, format="mp3", audio_bitrate="128k").run()


def process_file(file_path):
    # Check the file extension and process accordingly
    if file_path.endswith('.mp4'):
        video_to_mp3(file_path)
        file_name = "lecture_to_audio.mp3"
        file_path = os.path.join(os.getcwd(), file_name)
        if os.path.exists(file_path):
            return file_path
    elif file_path.endswith('.mp3'):
        if os.path.exists(file_path):
            return file_path
