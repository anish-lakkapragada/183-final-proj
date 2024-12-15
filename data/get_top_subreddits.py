"""
Script for fun to get the top 200 subreddits by size using Python Reddit Wrapper (PRAW).
"""
import praw
import os 

reddit = praw.Reddit(
    client_id=os.environ['CLIENT_ID'],
    client_secret=os.environ['CLIENT_SECRET'],
    user_agent=os.environ['USER_AGENT']
)

def fetch_top_subreddits(limit=200):
    try:
        top_subreddits = reddit.subreddits.popular(limit=limit)

        subreddit_data = [(subreddit.display_name, subreddit.subscribers) for subreddit in top_subreddits]

        sorted_subreddits = sorted(subreddit_data, key=lambda x: x[1], reverse=True)
        
        with open("data/top_200_subreddits.txt", "w") as file:
            file.write(f"{'Subreddit':<30} {'Subscribers':>10}\n")
            file.write(f"{'-' * 42}\n")
            for name, subscribers in sorted_subreddits:
                file.write(f"{name:<30} {subscribers:>10,}\n")
        
        print(f"Successfully wrote the top {limit} subreddits to 'top_subreddits.txt'.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Fetch and save the top 200 subreddits
fetch_top_subreddits()

