from flask import Flask
from pytube import YouTube
from moviepy.editor import concatenate_videoclips
from instabot import Bot
import os
import random
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Function to fetch trending short video IDs from YouTube using the YouTube API
def fetch_trending_short_ids():
    # Your logic to fetch trending short video IDs from YouTube
    # Example:
    trending_short_ids = ["short_video_id_1", "short_video_id_2", "short_video_id_3"]
    return trending_short_ids

# Function to download YouTube short
def download_short(short_id, output_dir):
    # Your logic to download a YouTube short with the given ID
    # Example:
    return True  # Return True if download is successful, False otherwise

# Function to create reels from downloaded shorts
def create_reels(downloaded_shorts_dir, output_path):
    # Your logic to concatenate downloaded shorts into a single reel
    # Example:
    return True  # Return True if reel creation is successful, False otherwise

# Function to read IDs of previously posted reels from a file
def read_posted_reels(filename):
    # Your logic to read IDs of previously posted reels from a file
    # Example:
    return []

# Function to write IDs of posted reels to a file
def write_posted_reels(posted_reels, filename):
    # Your logic to write IDs of posted reels to a file
    # Example:
    pass

# Function to fetch caption from YouTube shorts
def fetch_caption_from_shorts(short_id):
    try:
        url = f"https://www.youtube.com/shorts/{short_id}"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            caption_element = soup.find('meta', {'property': 'og:description'})
            if caption_element:
                caption = caption_element['content']
                return caption
        return ""
    except Exception as e:
        print(f"Error fetching caption from shorts: {e}")
        return ""

# Function to post reel on Instagram and send a direct message
def post_reel_on_instagram(username, password, reel_path, caption):
    try:
        bot = Bot()
        bot.login(username=username, password=password)

        # Add trending hashtags to the caption
        trending_hashtags = ["#trending", "#viral", "#explorepage"]
        caption_with_hashtags = f"{caption} {' '.join(trending_hashtags)}"

        # Post reel on Instagram
        bot.upload_video(reel_path, caption=caption_with_hashtags)

        # Send a direct message to yourself
        bot.send_message(os.getenv("INSTAGRAM_USERNAME"), f"Reel '{reel_path}' has been posted successfully!")

        print("Reel posted on Instagram and message sent successfully!")
        return True
    except Exception as e:
        print(f"Error posting reel on Instagram: {e}")
        return False

@app.route('/')
def post_reel():
    try:
        # Fetch trending short video IDs from YouTube
        trending_short_ids = fetch_trending_short_ids()

        # Select 1 unique random short ID
        random_short_ids = random.sample(trending_short_ids, 1)

        # Directory to save downloaded shorts
        output_dir = "downloaded_shorts"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Download and create reels for new shorts
        new_reel_created = False
        for short_id in random_short_ids:
            if download_short(short_id, output_dir):
                new_reel_created = True
        if new_reel_created:
            reel_output_path = "output_reel.mp4"
            if create_reels(output_dir, reel_output_path):
                # Fetch caption from the shorts
                caption_from_shorts = fetch_caption_from_shorts(random_short_ids[0])

                # Post reel on Instagram only if new reel is created
                posted_reels_filename = "posted_reels.txt"
                posted_reels = read_posted_reels(posted_reels_filename)
                if reel_output_path not in posted_reels:
                    username = os.getenv("INSTAGRAM_USERNAME")
                    password = os.getenv("INSTAGRAM_PASSWORD")
                    if post_reel_on_instagram(username, password, reel_output_path, caption_from_shorts):
                        posted_reels.append(reel_output_path)
                        write_posted_reels(posted_reels, posted_reels_filename)
                else:
                    print("Reel already posted. Skipping posting on Instagram.")
        else:
            print("No new reels created. Exiting program.")

        return 'Reel posted successfully!'
    except Exception as e:
        return f"Error posting reel: {e}"

if __name__ == '__main__':
    # Glitch expects the app to run on port 3000
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 3000)))
