import tweepy
import os
import random
from datetime import datetime
import shutil
import requests

# Paths and Globals
media_path = r"assets"
log = r"textfiles/logfile.txt"  # Ensure this path is correct and points to a valid log file
used_media_path = r"duplicateImages"
now = datetime.now()

# Ensure the log directory exists
if not os.path.exists(os.path.dirname(log)):
    os.makedirs(os.path.dirname(log))

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

# Choose a random image from the media path
def chooseRandomImage(path=media_path):
    files = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]
    if not files:
        raise ValueError("No files found in the specified path")
    choice = random.randint(0, len(files) - 1)
    return os.path.join(path, files[choice])

# Function to upload multiple media and create a tweet
def tweet(assets: list[str]) -> requests.Response:
    consumer_key = os.getenv('CONSUMER_KEY')
    consumer_secret = os.getenv('CONSUMER_SECRET')
    access_token = os.getenv('ACCESS_TOKEN')
    access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

    if not (consumer_key and consumer_secret and access_token and access_token_secret):
        raise EnvironmentError("Missing Twitter API credentials in environment variables")

    api_v1 = auth_v1(consumer_key, consumer_secret, access_token, access_token_secret)
    client_v2 = auth_v2(consumer_key, consumer_secret, access_token, access_token_secret)

    # Upload all media and get media IDs
    media_ids = [api_v1.media_upload(asset).media_id_string for asset in assets]

    # Create a tweet with the uploaded media IDs
    return client_v2.create_tweet(media_ids=media_ids)

# Main process
try:
    # Select a few random images (e.g., 3 images)
    num_images = 1
    images = [chooseRandomImage() for _ in range(num_images)]

    # Post tweet with the selected images
    response = tweet(images)

    # Move the used images to the 'duplicateImages' folder
    for img_path in images:
        shutil.move(img_path, os.path.join(used_media_path, os.path.basename(img_path)))

    # Log the image filenames and timestamp to the text file
    with open(log, 'a') as log_img:  # Corrected file mode
        for img_path in images:
            log_img.write(f"{os.path.basename(img_path)} {now.strftime('%d/%m/%Y %H:%M:%S')}\n")

    print(f"Tweeted successfully with media IDs: {', '.join(response.json()['data']['media_ids'])}")
except Exception as e:
    print(f"Error: {e}")
