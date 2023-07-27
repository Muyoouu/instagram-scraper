import json
from pandas import DataFrame
from datetime import datetime
 
 
# Function to convert datetime.datetime to excel serial date number
def excel_date(date1: datetime) -> float:
 
    # Initializing a reference date
    # Note that here date is not 31st Dec but 30th!
    temp = datetime(1899, 12, 30)

    delta = date1 - temp
    return float(delta.days) + (float(delta.seconds) / 86400)

if __name__ == "__main__":
    TARGET_USERNAME = "influencersinthewild"

    with open(rf"output/{TARGET_USERNAME}/{TARGET_USERNAME}_post.json", "r") as f:
        data = json.load(f)

    clean_data = []
    for post in data:
        select_data = dict()
        select_data["post_id"] = post["pk"]
        select_data["like_count"] = post["like_count"]
        select_data["comment_count"] = post["comment_count"]
        select_data["view_count"] = post["view_count"]

        # Change datetime format
        date_time_data = datetime.fromisoformat(post["taken_at"])
        date_time_data = date_time_data.replace(tzinfo=None)
        select_data["date_time"] = excel_date(date_time_data)
        select_data["day_of_the_week"] = date_time_data.strftime("%A")

        # Media type and URL extract
        if post["media_type"] == 1 or post["media_type"] == 2:
            select_data["thumbnail_url"] = post["thumbnail_url"]
            select_data["media_type"] = "picture" if post["media_type"] == 1 else "video"
        else:
            select_data["thumbnail_url"] = post["resources"][0]["thumbnail_url"]
            select_data["media_type"] = "album"
        
        clean_data.append(select_data)

    df = DataFrame.from_records(clean_data)
    df.to_csv(rf"output/{TARGET_USERNAME}/{TARGET_USERNAME}_post.csv")