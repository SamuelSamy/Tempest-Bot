from enum import Enum


class ModFormat(Enum):
    next_id         = "next-case-id"     
    logs            = "logs"
    mod_logs        = "mod-logs"
    channel         = "logs-channel"
    temp_mute       = "active-temp-mutes"
    temp_ban        = "active-temp-bans"
    a_punish        = "auto-punishments"
    a_punish_id     = "next-auto-punishment-id"
    permissions     = "permissions"


class CaseFormat(Enum):
    case_id     = "case_id"
    _type       = "type"
    reason      = "reason"
    time        = "time"
    moderator   = "moderator"
    duration    = "duration"


class AutoPunishment(Enum):
    id              = "id"
    time            = "time"
    warns           = "warns"
    flag            = "flag"
    flag_type       = "type"
    flag_duration   = "duration"


class Permissions(Enum):
    warn        = "warn"
    ban         = "ban"
    kick        = "kick"
    mute        = "warn"
    purge       = "purge"
    slowmode    = "slowmode"
    mod_logs    = "mod-logs"
    mod_stats   = "mod-stats"