class Case():
    
    def __init__(self, case_id, guild, user, _type, reason, time, moderator, duration):
        self.case_id     = case_id
        self.guild      = guild
        self.user        = user
        self._type       = _type
        self.reason      = reason
        self.time        = time
        self.moderator   = moderator
        self.duration    = duration
        self.expired     = False

    def __str__(self):
        return f"{self.case_id}  | {self.user}  |  {self._type}  |  {self.moderator}"