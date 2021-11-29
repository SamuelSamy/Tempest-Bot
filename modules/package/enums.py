from enum import Enum


class Settings(Enum):
    slowmode_channels    = "slowmode_channels" # [{}]
    lockdown_channels    = "lockdown_channels" # []
    
    lock_role            = "lock_role" # int
    
    scam_logs            = "scam_logs" # int

    muted_role           = "muted_role" # int
    
    helpers              = "helpers" # []
    helper_logs          = "helper_logs" # int
    helper_roles         = "helper_roles" # []

    suggestions_channels = "suggestions_channels" # []


class Colors(Enum):

    red     = 0xF40101
    green   = 0x46AF73
    blue    = 0x006AA3
    yellow  = 0xFDAD0D
    white   = 0xCCCCCC
    black   = 0xEFF7FA

