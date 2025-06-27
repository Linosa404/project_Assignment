import os
import json
from dotenv import load_dotenv
from atproto import Client
import requests
from datetime import datetime, timezone

load_dotenv()

# Retrieve Bluesky credentials from environment variables
USERNAME = os.getenv("BLUESKY_USERNAME")
PASSWORD = os.getenv("BLUESKY_PASSWORD")

# Define output directory and file for storing user posts
OUTPUT_DIR = "../Data"
OUTPUT_FILE_POSTS = os.path.join(OUTPUT_DIR, "user_posts.json")

def fetch_posts(post_limit=20):
    """
    Fetches the most recent posts from a user's Bluesky account and saves them as a JSON file.

    Parameters:
        post_limit (int): The number of recent posts to fetch. Default is 20.

    Output:
        A JSON file containing the user's posts is saved to the specified directory.
    """
    client = Client()
    client.login(USERNAME, PASSWORD)

    user_profile = client.get_profile(actor=USERNAME)
    print("DID:", user_profile.did)
    account_handle = user_profile.did

    print(f"Hole die letzten {post_limit} Posts von {account_handle}...")
    feed = client.get_author_feed(actor=account_handle, limit=post_limit)

    posts_data = [
        {
            "text": post.post.record.text,
            "created_at": post.post.record.created_at,
        }
        for post in feed.feed
    ]

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(OUTPUT_FILE_POSTS, "w", encoding="utf-8") as file:
        json.dump(posts_data, file, indent=4, ensure_ascii=False)

    print(f"Die Posts wurden erfolgreich in '{OUTPUT_FILE_POSTS}' gespeichert.")

def send_post(text):
    """
    Publishes a new post on Bluesky with the specified text content.

    Parameters:
        text (str): The content of the post to be published.

    Output:
        Prints the response from the Bluesky server after publishing the post.
    """
    client = Client()
    client.login(USERNAME, PASSWORD)

    pds_url = "https://bsky.social"

    resp = requests.post(
        pds_url + "/xrpc/com.atproto.server.createSession",
        json={"identifier": USERNAME, "password": PASSWORD},
        )
    resp.raise_for_status()
    session = resp.json()
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    post = {"$type": "app.bsky.feed.post",
            "text": text,
            "createdAt": now
            }

    resp = requests.post(
        pds_url + "/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": "Bearer " + session["accessJwt"]},
        json={
            "repo": session["did"],
            "collection": "app.bsky.feed.post",
            "record": post,
        },
    )
    print(json.dumps(resp.json(), indent=2))
    resp.raise_for_status()