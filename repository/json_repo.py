from enum import Flag
import json
from math import modf
from os import remove
from re import S

from domain.enums.general import Settings, Emotes
from domain.enums.leveling import Leveling
from domain.enums.moderation import BannedWord, ExternalLinks, ModFormat
from domain.exceptions import CustomException


class JsonRepository:

    def __init__(self, path):
        self._path = path


    def _open_json(self):
        with open(self._path) as file:
            data = json.load(file)

        return data


    def _save_json(self, data):
        with open(self._path, "w") as f:
            json.dump(data, f)
    

    def get_guild_data(self, guild_id):
        data = self._open_json()

        if str(guild_id) in data.keys():
            return data[str(guild_id)]
        
        return None


    def set_guild_data(self, guild_id, new_data):
        data = self._open_json()
        
        if str(guild_id) in data.keys():
            data[str(guild_id)] = new_data
            self._save_json(data)

    
    def init_data(self, guild_id, template, force_init = False):
        
        def fix_dict(initial_dict, template_dict):

            for key in template_dict.keys():
                if isinstance(template_dict[key], dict):
                    
                    if key not in initial_dict.keys():
                        initial_dict[key] = {}
                    
                    if len(template_dict[key].keys()) != 0:
                        fix_dict(initial_dict[key], template_dict[key])

                elif key not in initial_dict.keys():
                    initial_dict[key] = template_dict[key]



        data = self._open_json()
        guild_id = str(guild_id)

        if guild_id in data.keys() and force_init:
            fix_dict(data[guild_id], template)

        elif guild_id not in data.keys():
            data[guild_id] = template

        self._save_json(data)
        
    



class SettingsRepo(JsonRepository):

    def __init__(self):
        JsonRepository.__init__(self, "data/settings.json")


    def init_data(self, guild_id, force_init = False):
        JsonRepository.init_data(self, guild_id, JsonTemplates.settings_template, force_init)

    # STAFF RELATED COMMANDS
    def add_staff(self, guild_id, role_id):

        guild_data = JsonRepository.get_guild_data(self, guild_id)
        
        if role_id not in guild_data[Settings.staff_roles]:
            guild_data[Settings.staff_roles].append(role_id)
            answer = f"{Emotes.green_tick} Successfully added the specifed role to the staff roles!"
        else:
            answer = f"{Emotes.red_tick} This role already is already a staff role!"

        JsonRepository.set_guild_data(self, guild_id, guild_data)
        return answer


    def remove_staff(self, guild_id, role_id):

        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        
        if role_id in guild_data[Settings.staff_roles]:
            guild_data[Settings.staff_roles].remove(role_id)
            answer = f"{Emotes.green_tick} Successfully removed the specifed role from the staff roles!"
        else:
            answer = f"{Emotes.red_tick} This role is not a staff role!"

        JsonRepository.set_guild_data(self, guild_id, guild_data)
        return answer


    def get_staff_roles(self, guild_id):
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[Settings.staff_roles]
       

    # MUTE FUNCTIONS (get; set;)
    def get_muted_role(self, guild_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[Settings.muted_role]


    def set_muted_role(self, guild_id, role_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        guild_data[Settings.muted_role] = role_id
        JsonRepository.set_guild_data(self, guild_id, guild_data)


    # WELCOME FUNCTIONS

    def set_welcome_channel(self, guild_id, channel_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        guild_data[Settings.welcome_channel] = channel_id
        JsonRepository.set_guild_data(self, guild_id, guild_data)


    def get_welcome_channel(self, guild_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[Settings.welcome_channel]


    def set_welcome_message(self, guild_id, message):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        guild_data[Settings.welcome_message] = message
        JsonRepository.set_guild_data(self, guild_id, guild_data)


    def get_welcome_message(self, guild_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[Settings.welcome_message]
        

    # LOCKDOWN CHANNELS

    def get_lockdown_channels(self, guild_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[Settings.lockdown_channels]


    def add_lockdown_channel(self, guild_id, channel_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)

        if channel_id not in guild_data[Settings.lockdown_channels]:
            guild_data[Settings.lockdown_channels].append(channel_id)

        JsonRepository.set_guild_data(self, guild_id, guild_data)


    def remove_lockdown_channel(self, guild_id, channel_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)

        if channel_id in guild_data[Settings.lockdown_channels]:
            guild_data[Settings.lockdown_channels].remove(channel_id)

        JsonRepository.set_guild_data(self, guild_id, guild_data)


class LevelingRepo(JsonRepository):

    def __init__(self):
        JsonRepository.__init__(self, "data/leveling.json")


    def init_data(self, guild_id, force_init = False):
        JsonRepository.init_data(self, guild_id, JsonTemplates.leveling_tempalte, force_init)


    def get_no_xp_roles(self, guild_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[Leveling.no_xp_roles]


    def get_no_xp_channels(self, guild_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[Leveling.no_xp_channels]
    

    def get_time(self, guild_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[Leveling.time]


    def get_min_xp(self, guild_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[Leveling.min_xp]


    def get_max_xp(self, guild_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[Leveling.max_xp]


    # REWARDS FUNCTIONS
    def get_rewards(self, guild_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[Leveling.rewards]

    def add_reward(self, guild_id, level, role_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)

        if str(level) in guild_data[Leveling.rewards].keys():
            raise CustomException(f"{Emotes.wrong} This level already has a reward set!")

        guild_data[Leveling.rewards][str(level)] = role_id
        JsonRepository.set_guild_data(self, guild_id, guild_data)

    
    def remove_reward(self, guild_id, level):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)

        if str(level) not in guild_data[Leveling.rewards].keys():
            raise CustomException(f"{Emotes.wrong} This level does not have a reward!")

        del guild_data[Leveling.rewards][str(level)]
        JsonRepository.set_guild_data(self, guild_id, guild_data)


    # LEVEL UPS MESSAGES
    def get_notify_channel(self, guild_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[Leveling.notify_channel]


    def set_notify_channel(self, guild_id, channel_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        guild_data[Leveling.notify_channel] = channel_id
        JsonRepository.set_guild_data(self, guild_id, guild_data)


    # BLACKLIST
    def add_no_xp(self, guild_id, _type, _value, _object_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)

        if _object_id in guild_data[_type]:
            answer = f"{Emotes.not_found} This {_value.lower()} is already blacklisted!"
        else:
            guild_data[_type].append(_object_id)
            answer = f"{Emotes.green_tick} {_value} successfully blacklisted!"

        JsonRepository.set_guild_data(self, guild_id, guild_data)
        return answer

    def remove_no_xp(self, guild_id, _type, _value, _object_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)

        if _object_id not in guild_data[_type]:
            answer = f"{Emotes.not_found} This {_value.lower()} is not blacklisted!"
        else:
            guild_data[_type].remove(_object_id)
            JsonRepository.set_guild_data(self, guild_id, guild_data)
            answer = f"{Emotes.green_tick} The {_value.lower()} was successfully removed from the blacklist!"
        
        JsonRepository.set_guild_data(self, guild_id, guild_data)
        return answer

    
    def get_no_xp_channels(self, guild_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[Leveling.no_xp_channels]


    def get_no_xp_roles(self, guild_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[Leveling.no_xp_roles]

    # MULTIPLIERS
    
    def get_multipliers(self, guild_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[Leveling.multipliers]


    def set_multiplier(self, guild_id, role_id, value):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        guild_data[Leveling.multipliers][role_id] = value
        JsonRepository.set_guild_data(self, guild_id, guild_data)

    def remove_multiplier(self, guild_id, role_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)

        if str(role_id) not in guild_data[Leveling.multipliers].keys():
            raise CustomException(f"{Emotes.wrong} This role does not have a multiplier!")

        del guild_data[Leveling.multipliers][role_id]
        JsonRepository.set_guild_data(self, guild_id, guild_data)


class ModerationRepo(JsonRepository):

    def __init__(self):
        JsonRepository.__init__(self, "data/moderation.json")


    def init_data(self, guild_id, force_init = False):
        JsonRepository.init_data(self, guild_id, JsonTemplates.moderation_template, force_init)


    # STAFF RELATED FUNCTIONS
    def get_staff_permissions(self, guild_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[ModFormat.permissions]
    

    def allow_role(self, guild_id, role_id, _type):
        _type = _type.lower()
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        
        if _type not in guild_data[ModFormat.permissions]:
            answer = f"{Emotes.red_tick} That permission does not exist!"
        else:
            if role_id not in guild_data[ModFormat.permissions][_type]:
                guild_data[ModFormat.permissions][_type].append(role_id)
                answer = f"{Emotes.green_tick} Successfully added permission!"
            else:
                answer = f"{Emotes.red_tick} This role already has the specified permission!"

        return answer

    def remove_role(self, guild_id, role_id, _type):
        _type = _type.lower()
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)

        if _type not in guild_data[ModFormat.permissions]:
            answer = f"{Emotes.red_tick} That permission does not exist!"
        else:
            if role_id in guild_data[ModFormat.permissions][_type]:
                guild_data[ModFormat.permissions][_type].remove(role_id)
                answer = f"{Emotes.green_tick} Successfully removed permission!"
            else:
                answer = f"{Emotes.red_tick} This role does not have the specified permission!"

        return answer


    # BANNED WORDS FUNCTIONS
    def add_banned_word(self, guild_id, word_data):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)

        next_id = guild_data[ModFormat.next_bw_id]

        guild_data[ModFormat.next_bw_id] += 1
        guild_data[ModFormat.banned_words][str(next_id)] = word_data

        JsonRepository.set_guild_data(self, guild_id, guild_data)
        
    
    def remove_banned_word(self, guild_id, word_id):
        removed = False
        
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)

        if word_id in guild_data[ModFormat.banned_words].keys():
            del guild_data[ModFormat.banned_words][str(word_id)]
            JsonRepository.set_guild_data(self, guild_id, guild_data)
            removed = True

        return removed

    
    def get_banned_words(self, guild_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[ModFormat.banned_words]
    
    
    def set_notify_channel(self, guild_id, word_id, channel_id):
        channel_set = False

        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)


        if word_id in guild_data[ModFormat.banned_words].keys():
            guild_data[ModFormat.banned_words][str(word_id)][BannedWord.flags][BannedWord.flag_notify_channel] = channel_id
            JsonRepository.set_guild_data(self, guild_id, guild_data)
            channel_set = True
        
        return channel_set


    # LINK RELATED FUNCTIONS
    def allow_link(self, guild_id, _type, _object):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)

        if _object.id not in guild_data[ModFormat.links][_type]:
            guild_data[ModFormat.links][_type].append(_object.id)

        JsonRepository.set_guild_data(self, guild_id, guild_data)


    def block_link(self, guild_id, _type, _object):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)

        if _object.id in guild_data[ModFormat.links][_type]:
            guild_data[ModFormat.links][_type].remove(_object.id)

        JsonRepository.set_guild_data(self, guild_id, guild_data)


    def get_link_protected_channels(self, guild_id):  
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[ModFormat.links][ExternalLinks.protected_channels]


    def get_link_protected_roles(self, guild_id):
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[ModFormat.links][ExternalLinks.protected_roles]


    # MOD LOGS CHANNEL (get; set;)
    def get_mod_logs_channel(self, guild_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[ModFormat.mod_channel]


    def set_mod_logs_channel(self, guild_id, channel_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        guild_data[ModFormat.mod_channel] = channel_id
        JsonRepository.set_guild_data(self, guild_id, guild_data)


    # PUNISHMENTS
    def add_punishment(self, guild_id, new_punishment):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        next_id = guild_data[ModFormat.a_punish_id]
    
        guild_data[ModFormat.a_punish_id] += 1
        guild_data[ModFormat.a_punish][str(next_id)] = new_punishment

        JsonRepository.set_guild_data(self, guild_id, guild_data)

    def remove_punishment(self, guild_id, punishment_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)

        removed = False
        if punishment_id in guild_data[ModFormat.a_punish].keys():
            del guild_data[ModFormat.a_punish][str(punishment_id)]
            JsonRepository.set_guild_data(self, guild_id, guild_data)
            removed = True
    
        return removed

    
    def get_punishments(self, guild_id):
        guild_id = str(guild_id)
        guild_data = JsonRepository.get_guild_data(self, guild_id)
        return guild_data[ModFormat.a_punish]


class JsonTemplates:

    settings_template = {
        "muted-role": 0,
        "staff-roles": [],
        "welcome_message": "",
        "welcome_channel": 0,
        "lockdown_channels": []
    }


    leveling_tempalte = {
        "notify_channel": 0,
        "min_xp": 15,
        "max_xp": 40,
        "time": 60,
        "no_xp_roles": [],
        "no_xp_channels": [],
        "rewards": {},
        "multipliers": {
            "0": 1
        }
    }            


    moderation_template = {
        "next-case-id": 0,
        "next-bannedowrd-id": 0,
        "next-auto-punishment-id": 0,
        "logs-channel": 0,
        "permissions": {
            "warn": [],
            "ban": [],
            "kick": [],
            "mute": [],
            "purge": [],
            "slowmode": [],
            "delete-case": [],
            "mod-logs": [],
            "mod-stats": [],
            "lock": []
        },
        "auto-punishments": {},
        "banned_words": {},
        "external_links": {
            "protected_roles": [],
            "protected_channels": []
        }
    }