from praw import Reddit
from praw.models import Submission
import arrow
import redis
from comment_filters import RedditCommentFilter

class RedditCommentStream:
    
    subreddits = ["amitheasshole"]

    def __init__(self):
        
        user_agent_message = f'streaming comments from {RedditCommentStream.subreddits}'
        
        self.reddit = Reddit('comment_stream', user_agent=user_agent_message)
        
        self.subreddits_instance  = self.reddit.subreddit("+".join(RedditCommentStream.subreddits))

        self.redis = redis.Redis()
    
        self.comment_filter = RedditCommentFilter()

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




