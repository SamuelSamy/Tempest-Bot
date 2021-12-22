from enum import Enum


class ModFormat(Enum):
    next_id         = "next-case-id"     
    mod_channel     = "logs-channel"
    a_punish        = "auto-punishments"
    a_punish_id     = "next-auto-punishment-id"
    permissions     = "permissions"
    banned_words    = "banned_words"
    next_bw_id      = "next-bannedowrd-id"
    links           = "external_links"
    

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
    lock        = "lock"

class BannedWord(Enum):
    word                = "word"
    flags               = "flags"
    flag_type           = "type"
    flag_duration       = "duration"
    flag_notify_channel = "notify-channel"


class ExternalLinks(Enum):
    protected_roles     = "protected_roles"
    protected_channels  = "protected_channels"