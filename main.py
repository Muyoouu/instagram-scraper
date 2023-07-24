import logging
from logging import config
from instagrapi import Client
from instagrapi.exceptions import ClientBadRequestError, ClientConnectionError, ClientForbiddenError, GenericRequestError, ClientGraphqlError
from dotenv import load_dotenv, set_key, unset_key
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
    
    # Set IG Username to scrape
    TARGET_USERNAME = "influencersinthewild"
    # Set number of pages to scrape (non-negative integer), each page equals 50 items
    # Set to 0 to scrape all items in a profile
    TARGET_PAGE_NUMBERS = 0
    
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
            logger.info(f"Profile data of '{target_user_info['username']}' found, using saved data")
    except FileNotFoundError:
        logger.info(f"No profile data found, commencing new request of '{TARGET_USERNAME}' profile info")
        # Create directory if not exist
        if not path.exists(rf"{target_user_dir_path}"):
            makedirs(rf"{target_user_dir_path}")
        # Get and write target user info into new json file
        with open(rf"{profile_file_path}", "w") as f:
            target_user_info = cl.user_info_by_username(TARGET_USERNAME).dict()
            f.write(json.dumps(target_user_info, indent=4))
            logger.info(f"New profile data saved: '{profile_file_path}'")


    # Translate pages to items (each page have 50 items)
    # However, user total medias count is the maximum available item to scrape
    if TARGET_PAGE_NUMBERS == 0:
        target_item_numbers = target_user_info["media_count"]
    else:
        target_item_numbers = min(target_user_info["media_count"], TARGET_PAGE_NUMBERS * 50)

    # Check if there are stored end_cursor to resume
    end_cursor = environ.get(rf"{TARGET_USERNAME}_END_CURSOR")
    # Empty var for existing scraped items
    exist_scrape_items = list()
    if end_cursor:
        logger.info(f"Found 'end_cursor': '{end_cursor}' in cache, resuming latest scrape process")
        try:
            with open(rf"{target_user_dir_path}{TARGET_USERNAME}_post.json", "r") as f:
                # Load existing scraped data
                exist_scrape_items = json.load(f)
                # Adjust target items, consider exist scraped items
                target_item_numbers = min(target_user_info["media_count"] - len(exist_scrape_items), target_item_numbers)
                
                logger.info(f"User '{TARGET_USERNAME}' total medias: {target_user_info['media_count']} items")
                logger.info(f"Exist scraped data: {len(exist_scrape_items)} items inside '{target_user_dir_path}{TARGET_USERNAME}_post.json'")
                logger.info(f"Processing to scrape next {target_item_numbers} items")
        except FileNotFoundError:
            end_cursor = ""
            logger.info("No scraped data found, initializing new scrape process")
    else:
        end_cursor = ""
        logger.info("No 'end_cursor' data, initializing new scrape process")


    # Do scraping process
    posts = list()
    while True:
        try:
            # For backup purpose
            previous_end_cursor = end_cursor
            # Get user posts, "amount=0" means scrape all post
            page, end_cursor = cl.user_medias_paginated(target_user_info["pk"], amount=0, end_cursor=end_cursor)
            posts.extend(page)
            logger.info(f"Process: successfully scrape {len(posts)} out of {target_item_numbers} targeted items")
        # Handle connection error which may raise due to proxy being blocked
        except (ClientBadRequestError, ClientConnectionError, ClientForbiddenError, GenericRequestError, ClientGraphqlError):
            # Store the latest end_cursor to resume
            logger.exception(f"Scraping request failed, connection issue")
            if end_cursor:
                set_key(".env", rf"{TARGET_USERNAME}_END_CURSOR", rf"{end_cursor}")
                logger.info(f"Process Failed: scraped {len(posts)} out of {target_item_numbers} targeted items")
                logger.info(f"Process Failed: caching latest 'end_cursor':'{end_cursor}'")
            break
        
        # Quit loop if reach end of page or fulfilled scraping target
        if not end_cursor:
            logger.info(f"Process Finished: END OF PAGE, successfully scraped {len(posts)} items (target: {target_item_numbers})")
            if previous_end_cursor:
                set_key(".env", rf"{TARGET_USERNAME}_END_CURSOR", rf"{previous_end_cursor}")
                logger.info(f"Saving 'previous_end_cursor': '{previous_end_cursor}' in cache")
            else:
                if environ.get(rf"{TARGET_USERNAME}_END_CURSOR"):
                    unset_key(".env", rf"{TARGET_USERNAME}_END_CURSOR")
                    logger.info(f"Deleting '{TARGET_USERNAME}_END_CURSOR' from cache")
            break
        if len(posts) >= target_item_numbers:
            logger.info(f"Process Finished: REACH TARGET, successfully scraped {len(posts)} items (target: {target_item_numbers})")
            set_key(".env", rf"{TARGET_USERNAME}_END_CURSOR", rf"{end_cursor}")
            logger.info(f"Saving 'end_cursor': '{end_cursor}' in cache")
            break
    
    # Data formatting into json
    posts_dict = list()
    for post in posts:
        post = post.dict()
        post["taken_at"] = post["taken_at"].isoformat()
        posts_dict.append(post)
    
    # Merge new scrape data with exist scraped data from file
    if exist_scrape_items:
        posts_dict.extend(exist_scrape_items)

    # Write into json file
    with open(rf"{target_user_dir_path}{TARGET_USERNAME}_post.json", "w") as f:
        json.dump(posts_dict, f, indent=4)
        logger.info(f"Saving new scraped data: '{target_user_dir_path}{TARGET_USERNAME}_post.json'")
    