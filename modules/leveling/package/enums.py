from enum import Enum

class Leveling(Enum):
    level_up_channel    =   "level_up_channel"
    min_xp              =   "min_xp"
    max_xp              =   "max_xp"
    time                =   "time"
    no_xp_roles         =   "no_xp_roles"
    no_xp_channels      =   "no_xp_channels"
    rewards             =   "rewards"
    notify_channel      =   "notify_channel"


class FontColors(Enum):

    blue            =   (35, 24, 112, 255)
    white           =   (255, 255, 255, 255)
    almost_white    =   (230, 230, 230, 128) 
    gray            =   (100, 100, 100, 255)
    black           =   (10, 10, 9, 255)