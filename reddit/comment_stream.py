from praw import Reddit
from praw.models import Submission
import arrow
import redis
import os
from comment_filters import RedditCommentFilter

class RedditCommentStream:
    
    subreddits = ["amitheasshole"]

    def __init__(self):
        
        user_agent_message = f'streaming comments from {RedditCommentStream.subreddits}'
        
        self.reddit = Reddit('comment_stream', user_agent=user_agent_message)
        
        self.subreddits_instance  = self.reddit.subreddit("+".join(RedditCommentStream.subreddits))

        self.comment_filter = RedditCommentFilter()
        
        self._connect_db()

    def _connect_db(self):

        host = os.getenv('REDIS_HOST', 'localhost')
        port = os.getenv('REDIS_PORT', 6379)
        connected = False
        
        redis_client = redis.Redis(host=host, port=port) 
        while not connected:
            try:
                redis_client.ping()
            except Exception as e:
                print('Connection failed, trying again...')
                print(e)
                print(os.getenv('REDIS_HOST', 'NO HOST FOUND'))
                print(os.getenv('REDIS_PORT', 'NO PORT FOUND'))
            else:
                print('Connection successful')
                connected = True
        self.redis = redis_client

    def update_leaderboard(self, submission_id):
        
        if self.redis.exists(submission_id) == 0:
            
            submission = Submission(self.reddit, submission_id) 
            self.redis.hmset(submission_id, {
                "title": submission.title, 
                "created_ts": submission.created_utc,
                "url": submission.permalink,
                "flair": submission.link_flair_text if submission.link_flair_text else '' 
                })
            self.redis.publish("aita_comment_streams.new_submission", f"Creating new submission record: {submission_id}: {submission.title}")
        
        self.redis.zincrby("aita_leaderboard", 1, submission_id)
    
    def _get_submission_id(self, comment):
        parent_id = comment.parent_id
        return parent_id.split('_')[1]

    def start(self):

        for comment in self.subreddits_instance.stream.comments():
            
            if self.comment_filter.is_yta_judgement(comment):
                submission_id = self._get_submission_id(comment)
                self.redis.publish("aita_comment_streams.yta", f"Found a YTA: {comment.id}: {comment.body}")
                self.update_leaderboard(submission_id)
            self.redis.publish("aita_comment_streams.all", f"{comment.id}: {comment.body}")




