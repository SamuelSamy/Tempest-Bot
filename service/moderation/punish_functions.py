import time
import sqlite3
from repository.json_repo import ModerationRepo

import service.moderation.commands_functions as c_functions

from service._general.utils import *
from domain.enums.moderation import *
from domain.exceptions import CustomException


def add_punishment(guild, warns, time, _type, duration):
    
    if _type not in ['mute', 'ban', 'kick']:
        raise CustomException("Auto-punishment type must be `mute`, `kick` or `ban`")

    try:
        warns = int(warns)
    except:
        raise CustomException(f"{Emotes.wrong} The number of warns must be an integer!")

    if _type == 'kick' or duration == "" or duration == 0:
        duration = "0s"

    time_in_seconds = compute_seconds(time)
    punishment = {
        AutoPunishment.time: time_in_seconds,
        AutoPunishment.warns: warns,
        AutoPunishment.flags: {
            AutoPunishment.flag_type: _type,
            AutoPunishment.flag_duration: c_functions.compute_seconds(duration)
        } 
    }

    moderation_repo = ModerationRepo()
    moderation_repo.add_punishment(guild.id, punishment)

    

def remove_punishment(guild, punishment_id):
    
    moderation_repo = ModerationRepo()
    removed = moderation_repo.remove_punishment(guild.id, punishment_id)   
    
    if not removed:
        raise CustomException(f"{Emotes.wrong} No punishment found with the specified ID")


def list_punishments(guild):
    
    moderation_repo = ModerationRepo()
    punishments_dict = moderation_repo.get_punishments(guild.id)
    json_object = json.dumps(punishments_dict, indent = 4)
    return json_object


def get_punishments(guild):

    times = {}

    # TODO IDK IF IT WILL WORK
    punishments = list_punishments(guild)

    for punishment_id in punishments.keys():
        punishment_details = punishments[punishment_id]

        _time = str(punishment_details[AutoPunishment.time])
        
        if _time not in times.keys():
            times[_time] = []

        times[_time].append(punishment_details)
        
    return times


def count_warns(guild, user, _time):
    
    path = "data/database.db"
    table = "moderation_cases"

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(f"select * from {table} where guild = ? and user = ? and type = 'warn' and time + ? >= ?", (guild.id, user.id, _time, int(round(time.time()))))
    warns = len(cursor.fetchall())
    connection.close()

    return warns
    

async def apply_punishments(bot, channel, guild, user):
    
    times = get_punishments(guild)

    for _ in times.keys():

        _time = int(_)

        warns = count_warns(guild, user, _time)
    
        auto_punishments = times[_]

        auto_punishments.sort(reverse = True, key = lambda ap: ap[AutoPunishment.warns])

        for punishment in auto_punishments:
            p_warns = punishment[AutoPunishment.warns]
            if warns >= p_warns:
                _type = punishment[AutoPunishment.flags][AutoPunishment.flag_type]
                _duration = punishment[AutoPunishment.flags][AutoPunishment.flag_duration]
                await c_functions.handle_case(bot, guild, channel, bot.user, user, _type, f"Too many warns! ({p_warns} or more)", _duration)
                break