import os # To delete the temporary file
import csv # To read analytics data
import pandas as pd # To handle snippet selection
from pytube import YouTube # To downlaod the video
import moviepy.editor as mp # To crop videos
import transformers # To generate music
import scipy # To write wav files

def generate_music(destination, prompt="instagram tech video background music"):
    synthesiser = transformers.pipeline("text-to-audio", "facebook/musicgen-small")
    music = synthesiser(prompt)
    music2 = synthesiser(prompt)
    scipy.io.wavfile.write("audio_tmp.wav", rate=music["sampling_rate"], data=music["audio"])
    scipy.io.wavfile.write("audio_tmp2.wav", rate=music2["sampling_rate"], data=music2["audio"])
    audio_clip1 = mp.video.fx.all.fadeout(mp.AudioFileClip("audio_tmp.wav"), 3)
    audio_clip2 = mp.video.fx.all.fadein(mp.AudioFileClip("audio_tmp2.wav"), 3)
    audio_clip = mp.concatenate_audioclips([audio_clip1, audio_clip2])
    audio_clip.write_audiofile(destination)

    os.remove("audio_tmp.wav")
    os.remove("audio_tmp2.wav")

def crop_with_retention(url: str, retention_path: str, output_path = "ConvertedShort", max_seconds=60, deadzones=None):    
    # Gets important video metadata but does not download the mp4 file yet.
    video: YouTube = YouTube(url)
    seconds_per_percent = video.length/100

    with open(retention_path, "r") as file:
        csv_reader = csv.reader(file)
        # Get each moment's retention as a percent of the YouTube average at that time, skipping the header line.
        relative_retentions = [line[2] for line in csv_reader][1:]
    relative_retentions = [float(retention) for retention in relative_retentions]

    # The change in retention is more useful than the actual retention.
    retention_changes = [0]
    for i, retention in enumerate(relative_retentions[1:]):
        retention_changes.append(retention - relative_retentions[i])
    retention_changes = pd.Series(retention_changes)

    # Cut out deadzones that shouldn't be included in the final cut, such as advertisement reads.
    drops = []
    for deadzone in deadzones:
        lower_bound = int(deadzone[0] / seconds_per_percent)
        upper_bound = int(deadzone[1] / seconds_per_percent) + 1
        drops.extend(range(lower_bound, upper_bound+1))
    retention_changes.drop(drops, inplace=True)
    
    # Find the portions of the video with the best retention, getting as many as will fit into 1:00.
    max_snippets = int(max_seconds/seconds_per_percent)
    snippets = []
    num_snippets = 0
    while num_snippets < max_snippets:
        max = retention_changes.idxmax()
        # Convert percentage to actual timestamps
        snippets.append(max * seconds_per_percent)
        retention_changes.drop(max, inplace=True)
        num_snippets += 1
    snippets.sort()

    # Download the video. The file will be deleted after the function is done.
    print("Downloading original video...")
    stream_tag = video.streams.filter(file_extension="mp4")[0].itag
    stream = video.streams.get_by_itag(stream_tag)
    stream.download(filename="video_tmp.mp4")
    print("Original video downloaded.\n")

    #buffer_neg = seconds_per_percent / 2
    #buffer_pos = seconds_per_percent - buffer_neg
    print("Processing video...")
    with mp.VideoFileClip("video_tmp.mp4") as to_clip:
        # Get a couple seconds after each top timestamp and combine these clips into a video.
        #clips = [to_clip.subclip(snippet-buffer_neg, snippet+buffer_pos) for snippet in snippets]
        clips = [to_clip.subclip(snippet, snippet+seconds_per_percent) for snippet in snippets]
        best_clips = mp.concatenate_videoclips(clips)

        # Crop the video to 16:9 vertical format instead of horizontal
        vid_width = best_clips.size[0]
        vid_height = best_clips.size[1]
        new_width = int(9/16 * vid_height)
        x_center = int(vid_width / 2)
        y_center = int(vid_height / 2)
        cropped_video = best_clips.crop(x_center=x_center, y_center=y_center, width=new_width, height=vid_height)
        cropped_video = cropped_video.without_audio()
        video_length = cropped_video.duration

        for choice in range(1, 5):
            generate_music(f"audio_tmp.wav")
            audio_clip = mp.AudioFileClip(f"aduio_tmp.wav").subclip(0, video_length)
            combined_video = cropped_video.set_audio(audio_clip)
            combined_video.write(f"{output_path}-{choice}.mp4")
    
    os.remove("video_tmp.mp4")
    print("\nYour video is ready!")

if __name__ == "__main__":
    url = input("Enter the url of the video: ")
    path = input("Enter the file path to the retention data: ")
    output = input("Enter your preferred file name for the new video: ")
    print()
    deadzones = []
    print("Enter the beginning and end points of any deadzones that should not be in the video, in seconds. (ad reads, etc.)")
    print('Type "done" when done.')
    while True:
        start = input('Deadzone start (or "done"): ')
        if start == "done":
            print()
            break
        end = input("Deadzone end: ")
        deadzones.append((int(start), int(end)))
        print()
    crop_with_retention(url=url, retention_path=path, output_path=output, deadzones=deadzones)

'''
Recommended inputs:
https://www.youtube.com/watch?v=xYYLI6HvWL0&pp=ygUVaWYgaSBoYWQgYSA1MDAgZG9sbGFy  
Audience retention - If I had a $500 budget, this is what I'd build - Organic.csv
Short - If I had a $500 budget, this is what I'd build
36
42
420
465
done

'''