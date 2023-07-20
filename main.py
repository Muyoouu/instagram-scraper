from instagrapi import Client
from instagrapi.exceptions import ClientBadRequestError, ClientConnectionError, ClientForbiddenError, GenericRequestError, ClientGraphqlError
from dotenv import load_dotenv, set_key
from os import environ, path, makedirs

def album_download(client: Client, media: dict, folder: str ="") -> list[str]:

        assert media.get("media_type") == 8, "Must been album"
        paths = []
        for resource in media.get("resources"):
            filename = f"{media.get('user').get('username')}_{resource.get('pk')}"
            if resource.get("media_type") == 1:
                paths.append(
                    client.photo_download_by_url(resource.get("thumbnail_url"), filename, folder)
                )
            elif resource.get("media_type") == 2:
                paths.append(
                    client.video_download_by_url(resource.get("video_url"), filename, folder)
                )
            else:
                raise ValueError(
                    f'Media type "{resource.get("media_type")}" unknown for album (resource={resource.get("pk")})'
                )
        return paths

if __name__ == "__main__":
    import json
    
    TARGET_USERNAME = "influencersinthewild"
    TARGET_POST_NUMBER = 100
    
    # Set proxy
    cl = Client()
    load_dotenv()
    cl.set_proxy(f"http://scrapeops:{environ.get('API_KEY')}@proxy.scrapeops.io:5353")

    # Loads target user info data
    try:
        # Read target user info from existing json
        with open(rf"output/{TARGET_USERNAME}/{TARGET_USERNAME}_profile.json", "r") as f:
            target_user_info = json.load(f)
    except FileNotFoundError:
        # Create directory if not exist
        if not path.exists(rf"output/{TARGET_USERNAME}/"):
            makedirs(rf"output/{TARGET_USERNAME}/")
        # Get and write target user info into new json file
        with open(rf"output/{TARGET_USERNAME}/{TARGET_USERNAME}_profile.json", "w") as f:
            target_user_info = cl.user_info_by_username(TARGET_USERNAME).dict()
            f.write(json.dumps(target_user_info, indent=4))

    # Check if there are stored end_cursor to resume
    try:
        end_cursor = environ.get(rf"{TARGET_USERNAME}_END_CURSOR")
    except KeyError:
        end_cursor = ""

    # Do scraping process
    posts = list()
    while True:
        try:
            # Get user posts, "amount=0" means scrape all post
            page, end_cursor = cl.user_medias_paginated(target_user_info["pk"], amount=0, end_cursor=end_cursor)
            posts.extend(page)
        # Handle connection error which may raise due to proxy being blocked
        except (ClientBadRequestError, ClientConnectionError, ClientForbiddenError, GenericRequestError, ClientGraphqlError) as e:
            print(e)
            # Store the latest end_cursor to resume
            set_key(".env", rf"{TARGET_USERNAME}_END_CURSOR", rf"{end_cursor}")
            break
        
        # Quit loop if reach end of page or fulfilled scraping target
        if not end_cursor or len(posts) == TARGET_POST_NUMBER:
            break
    
    # Data formatting into json
    posts_dict = []
    for post in posts:
        post = post.dict()
        post["taken_at"] = post["taken_at"].isoformat()
        posts_dict.append(post)

    posts_json = json.dumps(posts_dict, indent=4)

    # Write into json file
    with open(rf"output/{TARGET_USERNAME}/{TARGET_USERNAME}_post.json", "a") as f:
        f.write(posts_json)
    