class Settings:
    slowmode_channels    = "slowmode-channels" # [{}]
    lockdown_channels    = "lockdown-channels" # []
    
    scam_logs            = "scam-logs" # int

    muted_role           = "muted-role" # int
    
    helper_logs          = "helper-logs" # int
    helper_roles         = "helper-roles" # []

    staff_roles          = "staff-roles" # []

    welcome_message      = "welcome_message"
    welcome_channel      = "welcome_channel"


class Colors:

    red     = 0xF40101
    green   = 0x46AF73
    blue    = 0x006AA3
    yellow  = 0xFDAD0D
    white   = 0xCCCCCC
    black   = 0xEFF7FA


class Emotes:
    red_tick        = "<:redTick:915333183715815444>"
    green_tick      = "<:greenTick:915333220726374461>"
    warn            = "⚠️"
    loading         = "<a:loading:915333280633598052>"
    orange_flag     = "<:OrangeFlag:915333566366367784>"
    no_entry        = "⛔"
    wrong           = "️️⁉️"
    not_found       = "💢"
    reply           = "<:reply:917177348988760095>"
    star            = "⭐"
