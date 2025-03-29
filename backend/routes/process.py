import os
import ffmpeg
from flask import session

filename = session.get("filename")
file_type = session.get("file_type")
match file_type:
    case "mp4":
        output_file = "lecture_to_audio.mp3"
        ffmpeg.input(filename).output(output_file, format="mp3", audio_bitrate="128k").run()
    case "mov":
        output_file = "lecture_to_audio.mp3"
        ffmpeg.input(filename).output(output_file, format="mp3", audio_bitrate="128k").run()
    case "mp3":
        output_file = "lecture_to_audio.mp3"
        os.rename(filename, output_file)
    # case "pptx":

    # case "pdf":
