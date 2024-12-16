"""
This is the script that will go through the top subreddits and their most recent posts and compile 
a CSV file which has information on (1) the number of off-topic ("shitpost") comments on a given post (2) the 
number of comments said post has (3) the upvote ratio of the post.
Specifically, the CSV file will have the following columns: 

subreddit post_id num_comments num_shitposts perc_shitposts upvote_ratio

for 200 subreddits * 100 posts/subreddit ≈ 20K rows, where each row represents a post. 
"""

from dotenv import load_dotenv
from datetime import datetime
import praw
from off_topic_detector import is_comment_off_topic
import pandas as pd
from tqdm import tqdm
import os
import time

load_dotenv()

NUM_TOP_SUBREDDITS = 200  # number of subreddits to look at, based on size
NUM_RECENT_POSTS = 100  # how many of the recent posts in each subreddit to analyze
MAX_COMMENTS_TO_REVIEW = 100  # max number of comments to review per post
MAX_CHARS = 150  # char limit for title + comment comparison for shitposting
FILE_EXPORT_NAME = "data/data_run_with_post_body.csv"

reddit = praw.Reddit(
    client_id=os.environ['CLIENT_ID'],
    client_secret=os.environ['CLIENT_SECRET'],
    user_agent=os.environ['USER_AGENT'],
    ratelimit_seconds=120
)

def get_subreddit_posting_data(subreddit, subreddit_name, num_previous_posts, max_comments_to_review):
    data_list = []
    try:
        subreddit = reddit.subreddit(subreddit_name)
        posts_on_this_subreddit = subreddit.new(limit=num_previous_posts)

        for submission in posts_on_this_subreddit:
            num_comments = min(submission.num_comments, max_comments_to_review)
            num_off_topic = 0
            submission.comments.replace_more(limit=None)  # Avoid fetching nested comments

            for c, comment in enumerate(submission.comments[:max_comments_to_review]):
                if is_comment_off_topic(submission.selftext[:MAX_CHARS] or submission.title[:MAX_CHARS], comment.body[:MAX_CHARS])[0]:
                    num_off_topic += 1

            data_list.append({
                'subreddit': subreddit_name,
                'post_id': submission.id,
                'num_comments': num_comments,
                'num_shitposts': num_off_topic,
                'perc_shitposts': None if num_comments == 0 else num_off_topic / num_comments,
                'upvote_ratio': submission.upvote_ratio, 
                'nsfw': subreddit.over18, 
                'subreddit_size': subreddit.subscribers,
                'creation_date': datetime.utcfromtimestamp(subreddit.created_utc).strftime('%m/%d/%y')
            })
    except Exception as e:
        print(f"An error occurred in subreddit '{subreddit_name}': {e}")
    
    return data_list

file_exists = os.path.exists(FILE_EXPORT_NAME)
top_subreddits = reddit.subreddits.popular(limit=NUM_TOP_SUBREDDITS)

for subreddit in tqdm(top_subreddits):

    subreddit_data = get_subreddit_posting_data(subreddit, subreddit.display_name, NUM_RECENT_POSTS, MAX_COMMENTS_TO_REVIEW)

    if subreddit_data:
        data_df = pd.DataFrame(subreddit_data)
        data_df.to_csv(FILE_EXPORT_NAME, mode='a', index=False, header=not file_exists)
        file_exists = True  

    time.sleep(2)
