import praw
import arrow

class RedditCommentStream:
    
    subreddits = ["amitheasshole"]

    def __init__(self):
        user_agent_message = f'streaming comments from {RedditCommentStream.subreddits}'
        self.reddit = praw.Reddit('comment_stream', user_agent=user_agent_message)
        """ 
        try:
            self.reddit
         except Exception as e:
             print('Could not connect to Reddit API.')
             self.reddit = None
        """
        self.subreddits_instance  = self.reddit.subreddit(
                "+".join(RedditCommentStream.subreddits)
                )

    def start(self):
        for comment in self.subreddits_instance.stream.comments():
            print(f"FOUND A COMMENT! {arrow.get(comment.created_utc)}:::{comment.body}")
