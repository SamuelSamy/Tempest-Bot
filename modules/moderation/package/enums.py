from enum import Enum

class ModFormat(Enum):
    next_id     = "next-case-id"     
    logs        = "logs"
    mod_logs    = "mod-logs"
    channel     = "logs-channel"
    temp_mute   = "active-temp-mutes"
    temp_ban    = "active-temp-bans"

class CaseFormat(Enum):
    case_id     = "case_id"
    _type       = "type"
    reason      = "reason"
    time        = "time"
    moderator   = "moderator"
    duration    = "duration"