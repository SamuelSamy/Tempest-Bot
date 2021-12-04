import time

import  modules.moderation.package.commands_functions as c_functions
from modules.package.utils import *
from modules.moderation.package.enums import *
from modules.package.exceptions import *


def add_punishment(guild, warns, time, _type, duration):
    
    if _type not in ['mute', 'ban', 'kick']:
        raise TypeException("Auto-punishment type must be `mute`, `kick` or `ban`")

    try:
        warns = int(warns)
    except:
        raise ValueError("The number of warns must be integer!")

    if _type == 'kick' or duration == "" or duration == 0:
        duration = "0s"
    
    json_file = open_json("data/moderation.json")

    guild_id = str(guild.id)
    next_id = json_file[guild_id][ModFormat.a_punish_id.value]
    time_in_seconds = compute_seconds(time)

    punishment = {
        AutoPunishment.time.value: time_in_seconds,
        AutoPunishment.warns.value: warns,
        AutoPunishment.flags.value: {
            AutoPunishment.flag_type.value: _type,
            AutoPunishment.flag_duration.value: c_functions.compute_seconds(duration)
        } 
    }

    json_file[guild_id][ModFormat.a_punish_id.value] += 1
    json_file[guild_id][ModFormat.a_punish.value][str(next_id)] = punishment

    save_json(json_file, "data/moderation.json")

    return True


def remove_punishment(guild, punishment_id):
    removed = False
    json_file = open_json("data/moderation.json")

    guild_id = str(guild.id)

    if punishment_id in json_file[guild_id][ModFormat.a_punish.value].keys():
        del json_file[guild_id][ModFormat.a_punish.value][str(punishment_id)]
        removed = True
    
    save_json(json_file, "data/moderation.json")
    return removed


def list_punishments(guild):
    
    json_file = open_json("data/moderation.json")

    guild_id = str(guild.id)

    punishments_dict = json_file[guild_id][ModFormat.a_punish.value]

    json_object = json.dumps(punishments_dict, indent = 4)

    return json_object


def get_punishments(guild):

    times = {}

    guild_id = str(guild.id)
    json_file = open_json("data/moderation.json")

    punishments = json_file[guild_id][ModFormat.a_punish.value]

    for punishment_id in punishments.keys():
        punishment_details = json_file[guild_id][ModFormat.a_punish.value][punishment_id]

        _time = str(punishment_details[AutoPunishment.time.value])
        
        if _time not in times.keys():
            times[_time] = []

        times[_time].append(punishment_details)
        
    return times


def count_warns(guild, user, _time):
    warns = 0

    guild_id = str(guild.id)
    user_id = str(user.id)
    json_file = open_json("data/moderation.json")

    user_cases = json_file[guild_id][ModFormat.logs.value][user_id]

    for case in user_cases:
        if case[CaseFormat._type.value] == 'warn':
            if case[CaseFormat.time.value] + _time  >= round(time.time()):
                warns += 1

    return warns


async def apply_punishments(bot, channel, guild, user):
    
    times = get_punishments(guild)

    for _ in times.keys():

        _time = int(_)

        warns = count_warns(guild, user, _time)
    
        auto_punishments = times[_]

        auto_punishments.sort(reverse = True, key = lambda ap: ap[AutoPunishment.warns.value])

        for punishment in auto_punishments:
            p_warns = punishment[AutoPunishment.warns.value]
            if warns >= p_warns:
                _type = punishment[AutoPunishment.flag.value][AutoPunishment.flag_type.value]
                _duration = punishment[AutoPunishment.flag.value][AutoPunishment.flag_duration.value]
                await c_functions.handle_case(bot, guild, channel, bot.user, user, _type, f"Too many warns! ({warns})", _duration)
                break