from instagrapi import Client
from dotenv import load_dotenv
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
        # Get and write target user info into new json file
        if not path.exists(rf"output/{TARGET_USERNAME}/"):
            makedirs(rf"output/{TARGET_USERNAME}/")
        with open(rf"output/{TARGET_USERNAME}/{TARGET_USERNAME}_profile.json", "w") as f:
            target_user_info = cl.user_info_by_username(TARGET_USERNAME).dict()
            f.write(json.dumps(target_user_info, indent=4))

    # Get user posts, "amount=0" means scrape all post
    posts = cl.user_medias(target_user_info["pk"], amount=0)
    
    # Data formatting into json
    posts_dict = []
    for post in posts:
        post = post.dict()
        post["taken_at"] = post["taken_at"].isoformat()
        posts_dict.append(post)

    posts_json = json.dumps(posts_dict, indent=4)

    # Write into json file
    with open(rf"output/{TARGET_USERNAME}/{TARGET_USERNAME}_post.json", "w") as f:
        f.write(posts_json)
        
    