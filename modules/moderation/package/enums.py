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
    banned_words    = "banned_words"
    next_bw_id      = "next-bannedowrd-id"
    links           = "external_links"


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
    flags           = "flags"
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


class BannedWord(Enum):
    word                = "word"
    flags               = "flags"
    flag_type           = "type"
    flag_duration       = "duration"
    flag_notify_channel = "notify-channel"


class ExternalLinks(Enum):
    protected_roles     = "protected_roles"
    protected_channels  = "protected_channels"