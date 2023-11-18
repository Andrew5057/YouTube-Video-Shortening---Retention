import moviepy.editor as mp

def combine_audio_video(destination: str, video_file: str, audio_file: str):
    video = mp.VideoFileClip(video_file)
    audio = mp.AudioFileClip(audio_file)
    combined = video.set_audio(audio)
    combined.write_videofile(f"{destination}.wav")