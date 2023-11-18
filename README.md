# Retention-based Video Cropping
This script takes in a retention graph for a YouTube video and isolates the highest-retention snippets as a 60-second video clip. It was created for Wendy and Devyn Johnston as a part of their AI Camp partnership.

## Usage Instructions
1. Download the retention graph for the desired video to the same folder as crop_video.py.
2. Run crop_video.py, ensuring the venv is active.
3. Paste the url of the YouTube video into the terminal.
4. Paste the name of the retention graph into the terminal.
5. Choose a name for the video that the script will produce. Try to avoid special characters (if you use them and the program crashes, just run it again without those characters.) You do not have to add .mp4 to the end of the name.
6. Enter the beginning and end points of deadzones. Deadzones are areas you don't want the program to consider, like ad reads. These should be integers representing the number of seconds since the start of the video (for example, if a deadzone starts at 4:30, you should eneter 270 as the deadzone start time.) Type "done" instead of the start time when you are done entering deadzones.

The video will be saved to the same folder as crop_video.py. It will be given the name [video name].mp4.

## Dependencies
All dependencies are included in requirements.txt.
Run on Python version 3.10.11. Dependencies will break otherwise.

## Known limitations
Videos produced with this method have awkward jump cuts. This is in part because the snippets are 1% of the video length, which often ends up being several seconds, and in part because the program does not understand natural breaks in speaking.

Videos produced with this method are not particularly content aware. This is because the program does not understand video structure. It is working purely off of user data.

Videos produced with this method must have acquired a substantial number of views. Otherwise, retention becomes an unreliable statistic off of which to base the excerption.
