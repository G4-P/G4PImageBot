import tweepy
import os
import random
from datetime import datetime
import shutil
import requests

# Paths and Globals

media_path = r"assets/videoTest"

log = r"textfiles/logfile.txt"  # Ensure this path is correct and points to a valid log file
used_media_path = r"duplicateImages"
now = datetime.now()

# Ensure the log directory exists
log_dir = os.path.dirname(log)
if not os.path.exists(log_dir):
    print(f"Creating log directory: {log_dir}")
    os.makedirs(log_dir)

# Authorize Twitter with v1.1 API for media uploads
def auth_v1(consumer_key, consumer_secret, access_token, access_token_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)

# Authorize Twitter with v2 API for tweet posting
def auth_v2(consumer_key, consumer_secret, access_token, access_token_secret):
    return tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        return_type=requests.Response,
    )

# Choose a random media (image or video) from the media path
def chooseRandomMedia():
    print(f"Current media_path list: {media_path}")
    
    # Randomly select one of the media directories
    selected_path = random.choice(media_path)
    print(f"Selected path: {selected_path}")

    # Ensure the path is valid and get the list of files in the selected directory
    if not os.path.exists(selected_path):
        raise FileNotFoundError(f"The directory does not exist: {selected_path}")

    files = [
        file for file in os.listdir(selected_path)
        if os.path.isfile(os.path.join(selected_path, file)) and file.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4', '.mov', '.avi'))
    ]
    
    if not files:
        raise ValueError(f"No valid media files found in the selected path: {selected_path}")
    
    # Randomly choose a file from the selected directory
    choice = random.randint(0, len(files) - 1)
    return os.path.join(selected_path, files[choice])

# Upload a media file (image or video) and return the media ID
def upload_media(api_v1, media_file):
    # Check file type to determine if it’s a video
    if media_file.lower().endswith(('.mp4', '.mov', '.avi')):
        print(f"Uploading video file: {media_file}")
        return api_v1.media_upload(filename=media_file, chunked=True).media_id_string
    else:
        print(f"Uploading image file: {media_file}")
        return api_v1.media_upload(filename=media_file).media_id_string

# Function to upload multiple media and create a tweet
def tweet(assets: list[str]) -> requests.Response:
    consumer_key = os.getenv('CONSUMER_KEY')
    consumer_secret = os.getenv('CONSUMER_SECRET')
    access_token = os.getenv('ACCESS_TOKEN')
    access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

    if not (consumer_key and consumer_secret and access_token and access_token_secret):
        raise EnvironmentError("Missing Twitter API credentials in environment variables")

    print("Authorizing Twitter API...")
    api_v1 = auth_v1(consumer_key, consumer_secret, access_token, access_token_secret)
    client_v2 = auth_v2(consumer_key, consumer_secret, access_token, access_token_secret)

    # Upload all media (images or videos) and get media IDs
    media_ids = [upload_media(api_v1, asset) for asset in assets]

    print(f"Uploaded media with IDs: {media_ids}")

    # Create a tweet with the uploaded media IDs
    return client_v2.create_tweet(media_ids=media_ids)

# Main process
try:
    # Select a few random media files (e.g., 1 media file)
    num_media = 1
    media_files = [chooseRandomMedia() for _ in range(num_media)]

    print(f"Selected media files: {media_files}")

    # Post tweet with the selected media files
    response = tweet(media_files)

    # Move the used media files to the 'duplicateImages' folder
    for media_file in media_files:
        used_media_full_path = os.path.join(used_media_path, os.path.basename(media_file))
        print(f"Moving {media_file} to {used_media_full_path}")
        if not os.path.exists(used_media_path):
            os.makedirs(used_media_path)
        shutil.move(media_file, used_media_full_path)

    # Log the media filenames and timestamp to the text file
    with open(log, 'a') as log_file:  # Corrected file mode
        for media_file in media_files:
            log_file.write(f"{os.path.basename(media_file)} {now.strftime('%d/%m/%Y %H:%M:%S')}\n")

    print(f"Tweeted successfully with media IDs: {', '.join(response.json()['data']['media_ids'])}")
except Exception as e:
    print(f"Error: {e}")
