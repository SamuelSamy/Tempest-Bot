from enum import Enum


class Settings(Enum):
    slowmode_channels    = "slowmode-channels" # [{}]
    lockdown_channels    = "lockdown-channels" # []
    
    lock_role            = "lock-role" # int
    
    scam_logs            = "scam-logs" # int

    muted_role           = "muted-role" # int
    
    helper_logs          = "helper-logs" # int
    helper_roles         = "helper-roles" # []

    suggestions_channels = "suggestions-channels" # []

    staff_roles          = "staff-roles" # []


class Colors(Enum):

    red     = 0xF40101
    green   = 0x46AF73
    blue    = 0x006AA3
    yellow  = 0xFDAD0D
    white   = 0xCCCCCC
    black   = 0xEFF7FA


class Emotes(Enum):
    red_tick    = "<:redTick:915333183715815444>"
    green_tick  = "<:greenTick:915333220726374461>"
    loading     = "<a:loading:915333280633598052>"
    orange_flag = "<:OrangeFlag:915333566366367784>"