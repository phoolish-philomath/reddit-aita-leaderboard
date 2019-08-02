class RedditCommentFilter:

    def is_yta_judgement(self, comment):
        return all([
            self._is_acceptable_user(comment),
            self._is_top_level_comment(comment),
            "YTA" in comment.body or "YWBTA" in comment.body
            ])
    
    def _is_acceptable_user(self, comment):
        return all([
            comment.author != 'AITAMod',
            not comment.stickied,
            not comment.is_submitter
            ])

    def _is_top_level_comment(self, comment):
        return comment.parent_id.startswith("t3")

