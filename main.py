from instagrapi import Client
from dotenv import load_dotenv
from os import environ

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
    
    cl = Client()

    # Set proxy
    load_dotenv()
    cl.set_proxy(f"http://scrapeops:{environ.get('API_KEY')}@proxy.scrapeops.io:5353")

    # Read target user info json
    with open("output/renebaebae_profile.json", "r") as f:
         target_user_info = json.load(f)

    # Get user posts
    posts = cl.user_medias(target_user_info["pk"], amount=50)
    
    # Data formatting into json
    posts_dict = []
    for post in posts:
         post = post.dict()
         post["taken_at"] = post["taken_at"].isoformat()
         posts_dict.append(post)

    posts_json = json.dumps(posts_dict, indent=4)

    # Write into json file
    with open("output/renebaebae_post.json", "w") as f:
         f.write(posts_json)
        
    