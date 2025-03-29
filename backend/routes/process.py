import os
import ffmpeg
from flask import session
from ..services import transcription, slides

filename = session.get("filename")
file_type = session.get("file_type")
output_file = "lecture_to_audio.mp3"
match file_type:
    case "mp4":
        ffmpeg.input(filename).output(output_file, format="mp3", audio_bitrate="128k").run()
        print(transcription.transcribe_audio(filename))
    case "mov":
        ffmpeg.input(filename).output(output_file, format="mp3", audio_bitrate="128k").run()
        print(transcription.transcribe_audio(filename))
    case "mp3":
        os.rename(filename, output_file)
        print(transcription.transcribe_audio(filename))
    # case "pptx":

    # case "pdf":
