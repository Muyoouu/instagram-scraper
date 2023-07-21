import logging
from logging import config
from instagrapi import Client
from instagrapi.exceptions import ClientBadRequestError, ClientConnectionError, ClientForbiddenError, GenericRequestError, ClientGraphqlError
from dotenv import load_dotenv, set_key
from os import environ, path, makedirs

# Log configuration dict
log_config = {
    "version":1,
    "root":{
        "handlers" : ["console", "file"],
        "level": "DEBUG"
    },
    "handlers":{
        "console":{
            "formatter": "std_out",
            "class": "logging.StreamHandler",
            "level": "DEBUG"
        },
        "file":{
            "formatter":"std_out",
            "class":"logging.FileHandler",
            "level":"DEBUG",
            "filename":"main.log"
        }
    },
    "formatters":{
        "std_out": {
            "format": "%(asctime)s -- %(levelname)s -- %(module)s -- %(message)s",
        }
    },
}
config.dictConfig(log_config)

# Create Logger
logger = logging.getLogger(__name__)


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
    target_user_dir_path = f"output/{TARGET_USERNAME}/"
    profile_file_path = f"{target_user_dir_path}{TARGET_USERNAME}_profile.json"
    try:
        # Read target user info from existing json
        with open(rf"{profile_file_path}", "r") as f:
            target_user_info = json.load(f)
            logger.info(f"Profile data of {target_user_info['username']} found, using saved data")
    except FileNotFoundError:
        logger.info(f"No profile data found, commencing new request of {TARGET_USERNAME} profile info")
        # Create directory if not exist
        if not path.exists(rf"{target_user_dir_path}"):
            makedirs(rf"{target_user_dir_path}")
        # Get and write target user info into new json file
        with open(rf"{profile_file_path}", "w") as f:
            target_user_info = cl.user_info_by_username(TARGET_USERNAME).dict()
            f.write(json.dumps(target_user_info, indent=4))
            logger.info(f"New profile data saved: '{profile_file_path}'")

    # Check if there are stored end_cursor to resume
    end_cursor = environ.get(rf"{TARGET_USERNAME}_END_CURSOR")
    if end_cursor:
        logger.info(f"Found 'end_cursor': '{end_cursor}' in cache, resuming latest scrape process")
    else:
        end_cursor = ""
        logger.info("Not found 'end_cursor' data, initializing new scrape process")

    # Do scraping process
    posts = list()
    while True:
        try:
            # Get user posts, "amount=0" means scrape all post
            page, end_cursor = cl.user_medias_paginated(target_user_info["pk"], amount=0, end_cursor=end_cursor)
            posts.extend(page)
            logger.info(f"Process: successfully scrape {len(posts)} out of {TARGET_POST_NUMBER} targeted items")
        # Handle connection error which may raise due to proxy being blocked
        except (ClientBadRequestError, ClientConnectionError, ClientForbiddenError, GenericRequestError, ClientGraphqlError):
            # Store the latest end_cursor to resume
            logger.exception(f"Scraping request failed, connection issue")
            if end_cursor:
                set_key(".env", rf"{TARGET_USERNAME}_END_CURSOR", rf"{end_cursor}")
                logger.info(f"Process Failed: scraped {len(posts)} out of {TARGET_POST_NUMBER} targeted items")
                logger.info(f"Process Failed: caching latest 'end_cursor':'{end_cursor}'")
            break
        
        # Quit loop if reach end of page or fulfilled scraping target
        if not end_cursor or len(posts) == TARGET_POST_NUMBER:
            logger.info(f"Process Finished: successfully scraped {len(posts)} items (target: {TARGET_POST_NUMBER})")
            break
    
    # Data formatting into json
    posts_dict = []
    for post in posts:
        post = post.dict()
        post["taken_at"] = post["taken_at"].isoformat()
        posts_dict.append(post)

    posts_json = json.dumps(posts_dict, indent=4)

    # Write into json file
    with open(rf"{target_user_dir_path}{TARGET_USERNAME}_post.json", "a") as f:
        f.write(posts_json)
        logger.info(f"Saved new scraped data: '{target_user_dir_path}{TARGET_USERNAME}_post.json'")
    