import csv, json
import tqdm
import googleapiclient.discovery
from collections import Counter
from itertools import chain

API_KEY = "AIzaSyD-POU93DLsqc863n3JUfPEr0Dyanda3VM"
def get_youtube_videos(query: str, n_pages: int):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)
    video_ids = []

    page_tokens = [None]
    for _ in tqdm.tqdm(range(n_pages), desc="Getting video ids"):
        search_response = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            videoCategoryId="28",  # Category ID for Technology
            pageToken = page_tokens[-1], 
            maxResults=50
        ).execute()

        # Extract video IDs from the search results
        video_ids.extend([item["id"].get("videoId") for item in search_response.get("items", []) if item["id"].get("videoId") is not None])
        page_tokens.append(search_response.get("nextPageToken"))
        if page_tokens[-1] in page_tokens[:-1]:
            print("\nOut of pages")
            break

    return video_ids

def add_youtube_ids_to_file(query: str, n_pages: int):
    ids = get_youtube_videos(query, n_pages)
    with open(f'video_ids_{query}.txt', "a+") as id_file:
        preexisting_ids = [id.strip() for id in id_file]
        for id in ids:
            if id not in preexisting_ids:
                id_file.write(id + "\n")

def get_youtube_tags_from_id(id: str):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)

    # Call the videos().list method to retrieve video details including tags
    video_response = youtube.videos().list(
        part="snippet",
        id=id
    ).execute()

    # Extract and print the tags
    if "items" in video_response:
        video = video_response["items"][0]
        tags = video["snippet"]["tags"] if "tags" in video["snippet"] else []
        return tags
    else:
        return []

def get_video_tags_from_id_file(id_file_name: str):
    with open(id_file_name, "r", encoding="utf-8") as id_file:
        video_ids = [id.strip() for id in id_file]
    with open(f"tags_for_{id_file_name}", "a", encoding="utf-8") as tag_file:
        for id in tqdm.tqdm(video_ids, desc="Getting tags"):
            tags = get_youtube_tags_from_id(id)
            if tags != []:
                tag_file.write(f"{id}: {tags}\n")

def get_top_tags(tag_file: str, threshold: int):
    with open(tag_file, "r", encoding="utf-8") as file:
        tag_lists = [eval(line.split(": ")[1]) for line in file]
    counter = Counter(chain.from_iterable(tag_lists))
    items = {}
    for tag, count in counter.items():
        if count >= threshold:
            if count in items:
                items[count].append(tag)
            else:
                items[count] = [tag]
    for count in sorted(items, reverse=True):
        print(f"{count}:\t{', '.join(items[count])}")

def get_transcript_from_id(video_id: str):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)
    transcript = youtube.captions().download(id=video_id).execute()
    return transcript
get_top_tags("tags_for_video_ids_pc build.txt", 25)