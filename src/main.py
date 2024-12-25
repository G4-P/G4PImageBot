import tweepy
import os
import random
from datetime import datetime
import shutil
import requests

# Paths and Globals

media_path = [r"assets/Ace wo Nerae", r"assets/Ace wo Nerae 2", r"assets/Ping Pong The Animation",
r"assets/Ashita no Nadja", r"assets/Planetes", r"assets/Plastic Nee-san", r"assets/School Rumble",
r"assets/Takarajima", r"assets/Teekyuu", r"assets/Teito Monogatari", r"assets/Tetsuwan Birdy OVA",
r"assets/Whisper of the Heart", r"assets/Yama no Sususme", r"assets/Yuru Yuri", r"assets/Cossette no Shouzou",
r"assets/Fumiko no Kokuhaku", r"assets/Hanamaru Youchien", r"assets/Hen Zemi", r"assets/Honneamise no Tsubasa",
r"assets/Koi Kaze", r"assets/Makasete Iruka", r"assets/Moetan", r"assets/Odd Taxi",
r"assets/TO", r"assets/Minami-ke", r"assets/Milky Holmes", r"assets/BRIGADOON Marin to Melan",r"assets/Kaiba", 
r"assets/Yuyushiki", r"assets/Ginga Tetsudou no Yoru", r"assets/Kodomo no Jikan", r"assets/Love Live School Idol Project",
r"assets/Memories", r"assets/Migi to Dali", r"assets/Mitsudomoe", r"assets/Popotan", r"assets/Birth", r"assets/Gankutsuou",
r"assets/Xenoglossia", r"assets/Made in Abyss"]

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

# Choose a random image or video from the media path

def chooseRandomMedia():
    # Randomly select one of the media directories
    selected_path = random.choice(media_path)
    
    # Ensure the path is valid and get the list of files in the selected directory
    files = [file for file in os.listdir(selected_path) if os.path.isfile(os.path.join(selected_path, file)) and file.lower().endswith(('.mp4', '.avi', '.mov', '.wmv', '.flv', '.jpg', '.jpeg', '.png', '.gif', '.bmp')) and len(file) > 1]
    
    if not files:
        raise ValueError(f"No files found in the selected path: {selected_path}")
    
    # Randomly choose a file from the selected directory
    choice = random.randint(0, len(files) - 1)
    selected_file = files[choice]
    
    # Check if the selected file exists
    if not os.path.exists(os.path.join(selected_path, selected_file)):
        raise FileNotFoundError(f"File not found: {selected_file}")
    
    return os.path.join(selected_path, selected_file)

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
    media_ids = []
    for asset in assets:
        if asset.lower().endswith(('.mp4', '.avi', '.mov', '.wmv', '.flv')):
            # Upload video file using chunked upload
            media_id = api_v1.chunked_upload(asset, media_category='tweet_video')
            media_ids.append(media_id.media_id_string)
        else:
            # Upload image file using media_upload
            media_id = api_v1.media_upload(asset)
            media_ids.append(media_id.media_id_string)

    # Create a tweet with the uploaded media IDs
    return client_v2.create_tweet(media_ids=media_ids)

# Main process
try:
    # Select a few random media (e.g., 1 media)
    num_media = 1
    media = [chooseRandomMedia() for _ in range(num_media)]

    # Post tweet with the selected media
    response = tweet(media)

    # Move the used media to the 'duplicateImages' folder
    for media_path in media:
        filename, file_extension = os.path.splitext(os.path.basename(media_path))
        new_path = os.path.join(used_media_path, filename + file_extension)
        shutil.move(media_path, new_path)

    # Log the media filenames and timestamp to the text file
    with open(log, 'a') as log_media:  # Corrected file mode
        for media_path in media:
            log_media.write(f"{os.path.basename(media_path)} {now.strftime('%d/%m/%Y %H:%M:%S')}\n")

    print(f"Tweeted successfully with media IDs: {', '.join(response.json()['data']['media_ids'])}")
except Exception as e:
    print(f"Error: {e}")
